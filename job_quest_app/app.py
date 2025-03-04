import sqlite3
import requests
import config
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database import save_job, get_saved_jobs, register_user, get_user_by_username
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Load secret key from .env

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Load user from database
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return User(id=user[0], username=user[1])
    return None

# Function to fetch jobs from Adzuna API
def fetch_jobs(job_title, location, job_type, page=1):
    url = f"https://api.adzuna.com/v1/api/jobs/{config.COUNTRY}/search/{page}?app_id={config.API_ID}&app_key={config.API_KEY}"
    
    params = {
        "what": job_title,
        "where": location,
        "results_per_page": 10
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get("results", [])
        job_list = []

        for job in data:
            job_info = {
                "Title": job.get("title", "Unknown"),
                "Company": job.get("company", {}).get("display_name", "Unknown"),
                "Location": job.get("location", {}).get("display_name", "Remote"),
                "Salary": f"${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}",
                "Type": job_type.capitalize(),
                "URL": job.get("redirect_url", "#")
            }
            job_list.append(job_info)

        return job_list
    else:
        print(f"API Error: {response.text}")
        return None 
    
# Base.html Footer Year
@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}    

# Homepage (Search Form)
@app.route("/")
def index():
    return render_template("index.html")

# Search Results Page
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # Handling the search form submission
        job_title = request.form["job_title"].strip()
        location = request.form["location"].strip()
        job_type = request.form["job_type"]
        page = 1  # Reset to first page on a new search

        # Validate input
        if not job_title:
            flash("Please enter a job title.", "error")
            return redirect(url_for("index"))
    
    else:  # GET request for pagination
        job_title = request.args.get("job_title", "").strip()
        location = request.args.get("location", "").strip()
        job_type = request.args.get("job_type", "")
        page = request.args.get("page", 1, type=int)  # Use current page from query string

    # Fetch job results
    jobs = fetch_jobs(job_title, location, job_type, page)

    if jobs is None:
        flash("Error retrieving job listings. Try again later.", "error")
        return redirect(url_for("index"))

    return render_template("results.html", jobs=jobs, job_title=job_title, location=location, job_type=job_type, page=page)


# Register User
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if register_user(username, password):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists. Choose another one.", "error")

    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)
        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1]))
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


# User Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# Search Page
@app.route("/search_page")
def search_page():
    return render_template("search.html")

# Forgout Password
@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")


# Save a job to SQLite (Only for logged-in users)
@app.route("/save_job", methods=["POST"])
@login_required
def save():
    title = request.form["title"]
    company = request.form["company"]
    location = request.form["location"]
    salary = request.form["salary"]
    job_type = request.form["job_type"]
    url = request.form["url"]
    user_id = current_user.id  # Get logged-in user ID

    save_job(title, company, location, salary, job_type, url, user_id)
    flash("Job saved successfully!", "success")
    return redirect(url_for("saved_jobs"))

# Delete a saved job (Only for logged-in users)
@app.route("/delete_job/<int:job_id>", methods=["POST"])
@login_required
def delete_job(job_id):
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_jobs WHERE id = ? AND user_id = ?", (job_id, current_user.id))
    conn.commit()
    conn.close()
    flash("Job removed successfully!", "success")
    return redirect(url_for("saved_jobs"))

# Display saved jobs (Only for logged-in users)
@app.route("/saved_jobs")
@login_required
def saved_jobs():
    jobs = get_saved_jobs(current_user.id)
    return render_template("saved_jobs.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True)
