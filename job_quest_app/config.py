import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Credentials
API_ID = os.getenv("API_ID")
API_KEY = os.getenv("API_KEY")
COUNTRY = os.getenv("COUNTRY", "us").strip()  # Default to 'us' if not set

# Flask Secret Key
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")

# Database Configuration
DATABASE_NAME = os.getenv("DATABASE_NAME", "jobs.db")

