# 🎮 Quiz-IT

A fun Django-based quiz platform where you can take quizzes, track your scores, and challenge yourself!  
Deployed live on Render for anyone to try.

---

## 🚀 Live Demo
[https://quiz-it-qyw0.onrender.com](https://quiz-it-qyw0.onrender.com)  

---

## ✨ Features
- **User Authentication:** Secure signup, login, and session management.
- **Interactive Quizzes:** Test your skills in Python, Java, C, and C# with real-time progress tracking and instant results.
- **Performance Dashboard:** Explore your past scores, see how you stack up on the **Leaderboard**, and view your score distribution via beautiful, interactive **Chart.js** graphs.
- **Manage Questions:** A clean, grid-based dashboard allowing users to easily add, edit, or delete multiple-choice questions for any subject.

---

## 🛠️ Tech Stack
- **Backend:** Python 3.13, Django 5.2.8
- **Frontend:** HTML5, CSS3, FontAwesome 6
- **Data Visualization:** Chart.js
- **Database:** SQLite3
- **Deployment:** Render, Gunicorn & Uvicorn, WhiteNoise (Static File Management)

---
  
## 🔮 Future Improvements
- Add timed quiz mode (countdown timers for added difficulty)
- Expand subject catalog and introduce difficulty levels
- Customizable user avatars and profiles
- Social sharing for high scores and quiz results

---

## 💻 Setup (Run Locally)

1. **Clone the repository:**
```bash
git clone https://github.com/jascify/Quiz-IT.git
cd Quiz-IT
```

2. **Create and activate a virtual environment:**
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Start the development server:**
```bash
python manage.py runserver


