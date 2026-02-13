# 🎮 Quiz-IT

A fun Django-based quiz platform where you can take quizzes, track your scores, and challenge yourself!  
Deployed live on Render for anyone to try.

---

## 🚀 Live Demo
[https://quiz-it-qyw0.onrender.com](https://quiz-it-qyw0.onrender.com)  

---

## 🛠️ Tech Stack
- **Python 3.13**  
- **Django 5.2.8**  
- **Gunicorn & Uvicorn**  
- **HTML & CSS**   
- **Render**  

---

## 💻 Setup (Run Locally)
```bash
git clone https://github.com/jascify/Quiz-IT.git
cd quiz_project
python -m venv .venv
# Activate virtual environment:
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
