import sqlite3
import requests
from flask import render_template
from datetime import datetime
from job_quest_app import app, config  

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

# Inject year for footer
@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}
