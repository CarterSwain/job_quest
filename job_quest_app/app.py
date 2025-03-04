from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from database import save_job, get_saved_jobs
import config
import sqlite3

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Load secret key from .env

# Function to fetch jobs from Adzuna API with pagination
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
                "Title": job.get("title", "Unknown"),  # Use .get() to avoid KeyErrors
                "Company": job.get("company", {}).get("display_name", "Unknown"),
                "Location": job.get("location", {}).get("display_name", "Remote"),
                "Salary": f"${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}",
                "Type": job_type.capitalize(),
                "URL": job.get("redirect_url", "#")  # Default to "#" if no URL is available
            }
            job_list.append(job_info)

        return job_list
    else:
        print(f"API Error: {response.text}")
        return None  # Return None if API call fails


# Homepage (Search Form)
@app.route("/")
def index():
    return render_template("index.html")

# Search Results Page
@app.route("/search", methods=["POST"])
def search():
    job_title = request.form["job_title"].strip()
    location = request.form["location"].strip()
    job_type = request.form["job_type"]
    page = request.args.get("page", 1, type=int)  # Get current page
    
    print(f"Received search request: title={job_title}, location={location}, type={job_type}")

    if not job_title:
        flash("Please enter a job title.", "error")
        return redirect(url_for("index"))

    jobs = fetch_jobs(job_title, location, job_type, page)

    if jobs is None:
        flash("Error retrieving job listings. Try again later.", "error")
        return redirect(url_for("index"))
    
    print(f"Jobs found: {len(jobs)}")

    return render_template("results.html", jobs=jobs, job_title=job_title, location=location, job_type=job_type, page=page)

# Save a job to SQLite
@app.route("/save_job", methods=["POST"])
def save():
    title = request.form["title"]
    company = request.form["company"]
    location = request.form["location"]
    salary = request.form["salary"]
    job_type = request.form["job_type"]
    url = request.form["url"]

    save_job(title, company, location, salary, job_type, url)
    flash("Job saved successfully!", "success")
    return redirect(url_for("saved_jobs"))

# Delete a saved job.
@app.route("/delete_job/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    flash("Job removed successfully!", "success")
    return redirect(url_for("saved_jobs"))


# Display saved jobs
@app.route("/saved_jobs")
def saved_jobs():
    jobs = get_saved_jobs()
    return render_template("saved_jobs.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True)
