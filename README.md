# 🚀 JobQuest - Job Search and Tracking App

JobQuest is a Flask-based web application that allows users to search for jobs using the Adzuna API, register/login, and save job listings for later reference.


---

## 🔥 Features

- 🔎  Search Jobs: Users can search for job listings using the **Adzuna API**.

- 📌 Save Jobs: Registered users can save job postings to track them later.
  
- 🔐 User Authentication: Register/Login securely with **Flask-Login** and **Flask-Bcrypt**.
  
- 📂 Database Storage: Uses SQLite for persisting user data and saved jobs.
  
- 🌐 Deployed on Render: Accessible online at: https://job-quest-7lfk.onrender.com/ 

---

## 🛠️ Installation & Setup

Clone the repo:
```bash
git clone https://github.com/carterswain/job_quest.git
cd jobquest
```

Set up Virutal Environment: 
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

Install Dependencies:
```bash
pip install -r requirements.txt
```

Create .env file and set up Env Variables:

API_ID=your_adzuna_api_id
API_KEY=your_adzuna_api_key
COUNTRY=us
SECRET_KEY=your_secret_key
DATABASE_NAME=jobs.db

Initialize Database: 
```bash
python -c "from job_quest_app.database import init_db; init_db()"
```

Run app locally:
```bash
flask run
```
OR with Gunicorn:
```bash
gunicorn job_quest_app.app:app
```
App will be available at:

http://127.0.0.1:5000/

---

📝 Future Improvements:

✅ Integrate third-party verification (Google, Github) for user registration.
✅ Improve UI design for a better experience.

---

🤝 Contributing
Want to improve this project?

Fork the repository
Create a feature branch (git checkout -b feature-name)
Commit changes (git commit -m "Added new feature")
Push to GitHub (git push origin feature-name)
Create a Pull Request 🎉

---

📜 License
This project is licensed under the MIT License.


