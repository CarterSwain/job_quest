import sqlite3
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from job_quest_app import app, bcrypt, User  # Import User from __init__.py
from job_quest_app.database import save_job, get_saved_jobs, register_user, get_user_by_username
from job_quest_app.app import fetch_jobs  # Import fetch_jobs from app.py

# Homepage (Search Form)
@app.route("/")
def index():
    return render_template("index.html")

# Search Results Page
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        job_title = request.form["job_title"].strip()
        location = request.form["location"].strip()
        job_type = request.form["job_type"]
        page = 1  # Reset to first page on a new search

        if not job_title:
            flash("Please enter a job title.", "error")
            return redirect(url_for("index"))
    
    else:
        job_title = request.args.get("job_title", "").strip()
        location = request.args.get("location", "").strip()
        job_type = request.args.get("job_type", "")
        page = request.args.get("page", 1, type=int)

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
            flash("Username already exists.", "error")

    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)
        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1]))  # ✅ Correct usage of User class
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

# Forgot Password
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
    conn = sqlite3.connect("jobs.db")  # ✅ Use SQLite database correctly
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
