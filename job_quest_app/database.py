import sqlite3
from flask_bcrypt import Bcrypt

DB_NAME = "jobs.db"
bcrypt = Bcrypt()

def init_db():
    """Initialize the database and create tables for users and saved jobs."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Modify saved_jobs table to associate jobs with users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            url TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def save_job(title, company, location, salary, job_type, url, user_id):
    """Save a job to the database, associated with the logged-in user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_jobs (title, company, location, salary, job_type, url, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, company, location, salary, job_type, url, user_id))
    conn.commit()
    conn.close()

def get_saved_jobs(user_id):
    """Retrieve all saved jobs for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_jobs WHERE user_id = ?", (user_id,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def register_user(username, password):
    """Register a new user with a hashed password."""
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True  # Registration successful
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieve user details by username."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns None if user is not found

# Initialize the database
init_db()
