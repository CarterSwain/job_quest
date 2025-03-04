import sqlite3

DB_NAME = "jobs.db"

def init_db():
    """Initialize the database and create a table for saved jobs."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            url TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_job(title, company, location, salary, job_type, url):
    """Save a job to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_jobs (title, company, location, salary, job_type, url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, company, location, salary, job_type, url))
    conn.commit()
    conn.close()

def get_saved_jobs():
    """Retrieve all saved jobs."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_jobs")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Initialize the database
init_db()
