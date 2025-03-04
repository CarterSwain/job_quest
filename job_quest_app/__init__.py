import sqlite3
from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from job_quest_app.config import SECRET_KEY, DATABASE_NAME  

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Load secret key

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

# Define the User class BEFORE using it
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return User(id=user[0], username=user[1])
    return None

from job_quest_app import routes
