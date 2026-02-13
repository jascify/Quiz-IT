import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import sqlite3
from datetime import datetime
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os


class Database:
    def __init__(self, db_name="quiz_app.db"):
        # Delete existing database to start fresh
        if os.path.exists(db_name):
            os.remove(db_name)

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_option INTEGER NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        self.conn.commit()

        # Always add default questions
        self.add_default_questions()

    def add_default_questions(self):
        default_questions = [
            # Python Questions
            ("Python", "Which keyword is used to define a function in Python?", "function", "def", "func", "define", 2),
            ("Python", "What is the correct file extension for Python files?", ".pyth", ".pt", ".py", ".pyt", 3),
            ("Python", "Which Python data structure is mutable and ordered?", "tuple", "set", "list", "frozenset", 3),
            ("Python", "Which of these is used to create objects in Python?", "new", "create", "class constructor",
             "object()", 3),
            ("Python", "Which method is called when an object is created in Python?", "__init__", "__new__",
             "constructor", "create", 1),

            # Java Questions
            ("Java", "Which of these is NOT a primitive data type in Java?", "int", "boolean", "String", "char", 3),
            ("Java", "What does JVM stand for?", "Java Virtual Machine", "Java Variable Method", "Java Visual Machine",
             "Just Virtual Machine", 1),
            ("Java", "What keyword is used to inherit a class in Java?", "inherits", "extends", "implements", "inherit",
             2),
            ("Java", "What is the default value of a boolean in Java?", "true", "false", "0", "null", 2),
            ("Java", "What is the parent class of all exceptions in Java?", "Exception", "Throwable", "Error",
             "RuntimeException", 2),

            # C Questions
            ("C", "Which operator is used for comments in C?", "#", "//", "/*", "Both // and /*", 4),
            ("C", "What is the size of int in C (typically)?", "2 bytes", "4 bytes", "8 bytes", "Depends on compiler",
             2),
            ("C", "Which header file is used for input/output in C?", "iostream.h", "stdio.h", "input.h", "output.h",
             2),
            ("C", "Which function is used to allocate memory dynamically in C?", "alloc()", "malloc()", "new()",
             "memory()", 2),
            ("C", "Which operator is used to access structure members in C?", "->", ".", ":", "Both -> and .", 4),

            # C# Questions
            ("C#", "Which access modifier makes a member accessible only within the same class in C#?", "public",
             "private", "protected", "internal", 2),
            ("C#", "What is the base class of all classes in C#?", "System.Base", "Object", "System.Object",
             "BaseClass", 3),
            ("C#", "What is the correct syntax to output 'Hello World' in C#?", "print('Hello World');",
             "Console.WriteLine('Hello World');", "System.out.println('Hello World');", "cout << 'Hello World';", 2),
            ("C#", "What is the keyword for exception handling in C#?", "catch", "try", "throw", "All of these", 4),
            ("C#", "What is the correct way to declare a constant in C#?", "const int x = 10;", "final int x = 10;",
             "constant int x = 10;", "readonly x = 10;", 1)
        ]

        try:
            self.cursor.executemany(
                "INSERT INTO questions (subject, question, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
                default_questions
            )
            self.conn.commit()
            print(f"Successfully added {len(default_questions)} questions to database")
        except Exception as e:
            print(f"Error adding questions: {e}")

    def get_all_questions(self):
        self.cursor.execute("SELECT * FROM questions")
        result = self.cursor.fetchall()
        print(f"Total questions in database: {len(result)}")
        return result

    def get_questions_by_subject(self, subject):
        self.cursor.execute("SELECT * FROM questions WHERE subject=?", (subject,))
        result = self.cursor.fetchall()
        print(f"Questions for {subject}: {len(result)}")
        return result

    def get_subjects(self):
        self.cursor.execute("SELECT DISTINCT subject FROM questions ORDER BY subject")
        result = [row[0] for row in self.cursor.fetchall()]
        print(f"Available subjects: {result}")
        return result

    def add_question(self, subject, question, options, correct):
        self.cursor.execute(
            "INSERT INTO questions (subject, question, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (subject, question, options[0], options[1], options[2], options[3], correct + 1)
        )
        self.conn.commit()

    def update_question(self, q_id, subject, question, options, correct):
        self.cursor.execute(
            "UPDATE questions SET subject=?, question=?, option1=?, option2=?, option3=?, option4=?, correct_option=? WHERE id=?",
            (subject, question, options[0], options[1], options[2], options[3], correct + 1, q_id)
        )
        self.conn.commit()

    def delete_question(self, q_id):
        self.cursor.execute("DELETE FROM questions WHERE id=?", (q_id,))
        self.conn.commit()

    def save_score(self, name, subject, score, total, percentage, date):
        self.cursor.execute(
            "INSERT INTO scores (name, subject, score, total, percentage, date) VALUES (?, ?, ?, ?, ?, ?)",
            (name, subject, score, total, percentage, date)
        )
        self.conn.commit()

    def get_all_scores(self):
        self.cursor.execute("SELECT * FROM scores")
        return self.cursor.fetchall()

    def get_user_scores(self, name):
        self.cursor.execute("SELECT * FROM scores WHERE name=? ORDER BY date", (name,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Programming Quiz Application")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")

        print("Initializing database...")
        self.db = Database()

        self.current_user = None
        self.current_subject = None
        self.current_question_index = 0
        self.user_answers = []
        self.score = 0
        self.questions = []
        self.subject_filter = None

        # Verify database has data
        all_questions = self.db.get_all_questions()
        subjects = self.db.get_subjects()
        print(f"Database initialized with {len(all_questions)} questions")
        print(f"Available subjects: {subjects}")

        self.show_home_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_home_page(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(frame, text="Programming Quiz", font=("Arial", 32, "bold"),
                         bg="#1a1a2e", fg="#00fff5")
        title.pack(pady=20)

        subtitle = tk.Label(frame, text="Python | Java | C | C#", font=("Arial", 14),
                            bg="#1a1a2e", fg="#00fff5")
        subtitle.pack(pady=10)

        btn_style = {"font": ("Arial", 14), "width": 20, "height": 2,
                     "bg": "#0f3460", "fg": "white", "border": 0, "cursor": "hand2"}

        tk.Button(frame, text="Start Quiz", command=self.start_quiz, **btn_style).pack(pady=10)
        tk.Button(frame, text="View Performance", command=self.show_performance_menu, **btn_style).pack(pady=10)
        tk.Button(frame, text="Manage Questions", command=self.manage_questions, **btn_style).pack(pady=10)
        tk.Button(frame, text="Exit", command=self.root.quit, **btn_style).pack(pady=10)

    def start_quiz(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Enter Your Name", font=("Arial", 20),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        name_entry = tk.Entry(frame, font=("Arial", 14), width=30)
        name_entry.pack(pady=10)

        def submit_name():
            name = name_entry.get().strip()
            if name:
                self.current_user = name
                self.choose_subject()
            else:
                messagebox.showerror("Error", "Please enter your name")

        tk.Button(frame, text="Next", command=submit_name, font=("Arial", 14),
                  bg="#0f3460", fg="white", width=15, height=2).pack(pady=20)

    def choose_subject(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text=f"Welcome, {self.current_user}!", font=("Arial", 20),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        tk.Label(frame, text="Choose Subject", font=("Arial", 18),
                 bg="#1a1a2e", fg="white").pack(pady=10)

        subjects = self.db.get_subjects()
        print(f"Displaying {len(subjects)} subjects: {subjects}")

        if not subjects:
            messagebox.showerror("Error", "No subjects available. Database error!")
            self.show_home_page()
            return

        btn_style = {"font": ("Arial", 14), "width": 20, "height": 2,
                     "bg": "#0f3460", "fg": "white"}

        for subject in subjects:
            btn = tk.Button(frame, text=subject,
                            command=lambda s=subject: self.start_subject_quiz(s),
                            **btn_style)
            btn.pack(pady=8)
            print(f"Created button for subject: {subject}")

        tk.Button(frame, text="Back", command=self.show_home_page,
                  font=("Arial", 12), bg="#16213e", fg="white",
                  width=15, height=1).pack(pady=20)

    def start_subject_quiz(self, subject):
        print(f"Starting quiz for subject: {subject}")
        self.current_subject = subject
        self.current_question_index = 0
        self.user_answers = []
        self.score = 0
        self.questions = self.db.get_questions_by_subject(subject)

        if not self.questions:
            messagebox.showinfo("Info", f"No questions available for {subject}")
            self.choose_subject()
            return

        self.display_question()

    def display_question(self):
        if self.current_question_index >= len(self.questions):
            self.show_result()
            return

        self.clear_window()

        question = self.questions[self.current_question_index]

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both", padx=50, pady=50)

        subject_label = tk.Label(frame, text=f"Subject: {self.current_subject}",
                                 font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#00fff5")
        subject_label.pack(pady=5)

        progress = tk.Label(frame, text=f"Question {self.current_question_index + 1} of {len(self.questions)}",
                            font=("Arial", 12), bg="#1a1a2e", fg="#00fff5")
        progress.pack(pady=10)

        q_label = tk.Label(frame, text=question[2], font=("Arial", 18),
                           bg="#1a1a2e", fg="white", wraplength=700)
        q_label.pack(pady=30)

        self.selected_option = tk.IntVar(value=-1)

        options = [question[3], question[4], question[5], question[6]]
        for i, option in enumerate(options):
            rb = tk.Radiobutton(frame, text=option, variable=self.selected_option, value=i,
                                font=("Arial", 14), bg="#1a1a2e", fg="white",
                                selectcolor="#0f3460", activebackground="#1a1a2e",
                                activeforeground="white")
            rb.pack(anchor="w", padx=100, pady=8)

        btn_frame = tk.Frame(frame, bg="#1a1a2e")
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Next", command=self.next_question,
                  font=("Arial", 14), bg="#0f3460", fg="white",
                  width=15, height=2).pack()

    def next_question(self):
        if self.selected_option.get() == -1:
            messagebox.showwarning("Warning", "Please select an answer")
            return

        question = self.questions[self.current_question_index]
        selected = self.selected_option.get()
        self.user_answers.append(selected)

        if selected == question[7] - 1:
            self.score += 1

        self.current_question_index += 1
        self.display_question()

    def show_result(self):
        self.clear_window()

        percentage = (self.score / len(self.questions)) * 100

        self.db.save_score(
            self.current_user,
            self.current_subject,
            self.score,
            len(self.questions),
            percentage,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Quiz Completed!", font=("Arial", 28, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        tk.Label(frame, text=f"Name: {self.current_user}", font=("Arial", 16),
                 bg="#1a1a2e", fg="white").pack(pady=5)
        tk.Label(frame, text=f"Subject: {self.current_subject}", font=("Arial", 16),
                 bg="#1a1a2e", fg="white").pack(pady=5)
        tk.Label(frame, text=f"Score: {self.score}/{len(self.questions)}",
                 font=("Arial", 16), bg="#1a1a2e", fg="white").pack(pady=5)
        tk.Label(frame, text=f"Percentage: {percentage:.1f}%", font=("Arial", 16),
                 bg="#1a1a2e", fg="white").pack(pady=5)

        if percentage >= 80:
            remark = "Excellent! 🎉"
            color = "#00ff00"
        elif percentage >= 60:
            remark = "Good Job! 👍"
            color = "#ffff00"
        else:
            remark = "Keep Practicing! 💪"
            color = "#ff6b6b"

        tk.Label(frame, text=remark, font=("Arial", 18, "bold"),
                 bg="#1a1a2e", fg=color).pack(pady=10)

        tk.Button(frame, text="Back to Home", command=self.show_home_page,
                  font=("Arial", 14), bg="#0f3460", fg="white",
                  width=15, height=2).pack(pady=30)

    def show_performance_menu(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Performance Menu", font=("Arial", 24, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=30)

        btn_style = {"font": ("Arial", 14), "width": 25, "height": 2,
                     "bg": "#0f3460", "fg": "white"}

        tk.Button(frame, text="View My Past Scores",
                  command=self.view_my_scores, **btn_style).pack(pady=10)
        tk.Button(frame, text="View Leaderboard",
                  command=self.view_leaderboard, **btn_style).pack(pady=10)
        tk.Button(frame, text="View Score Distribution",
                  command=self.view_distribution, **btn_style).pack(pady=10)
        tk.Button(frame, text="Back to Home",
                  command=self.show_home_page, **btn_style).pack(pady=10)

    def view_my_scores(self):
        name = simpledialog.askstring("Input", "Enter your name:")
        if not name:
            return

        user_scores = self.db.get_user_scores(name)

        if not user_scores:
            messagebox.showinfo("Info", "No scores found for this user")
            return

        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text=f"Performance History - {name}", font=("Arial", 20, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        fig = plt.Figure(figsize=(8, 5), facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f3460")

        attempts = np.arange(1, len(user_scores) + 1)
        percentages = [score[5] for score in user_scores]

        ax.plot(attempts, percentages, marker='o', color="#00fff5", linewidth=2, markersize=8)
        ax.fill_between(attempts, percentages, alpha=0.3, color="#00fff5")
        ax.set_xlabel("Attempt Number", color="white", fontsize=12)
        ax.set_ylabel("Score (%)", color="white", fontsize=12)
        ax.set_title(f"Performance Trend - {name}", color="white", fontsize=14)
        ax.tick_params(colors="white")
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        tk.Button(frame, text="Back", command=self.show_performance_menu,
                  font=("Arial", 12), bg="#0f3460", fg="white",
                  width=15, height=2).pack(pady=10)

    def view_leaderboard(self):
        scores = self.db.get_all_scores()

        if not scores:
            messagebox.showinfo("Info", "No scores available")
            return

        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="Leaderboard - Top 10", font=("Arial", 20, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        sorted_scores = sorted(scores, key=lambda x: x[5], reverse=True)[:10]

        fig = plt.Figure(figsize=(8, 5), facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f3460")

        names = [f"{score[1][:10]} ({score[2]})" for score in sorted_scores]
        percentages = [score[5] for score in sorted_scores]

        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(names)))
        bars = ax.barh(names, percentages, color=colors)
        ax.set_xlabel("Score (%)", color="white", fontsize=12)
        ax.set_title("Top Performers", color="white", fontsize=14)
        ax.tick_params(colors="white")
        ax.invert_yaxis()

        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.1f}%',
                    ha='left', va='center', color='white', fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        tk.Button(frame, text="Back", command=self.show_performance_menu,
                  font=("Arial", 12), bg="#0f3460", fg="white",
                  width=15, height=2).pack(pady=10)

    def view_distribution(self):
        scores = self.db.get_all_scores()

        if not scores:
            messagebox.showinfo("Info", "No scores available")
            return

        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="Score Distribution", font=("Arial", 20, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        fig = plt.Figure(figsize=(8, 5), facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f3460")

        percentages = np.array([score[5] for score in scores])

        n, bins, patches = ax.hist(percentages, bins=10, color="#00fff5", edgecolor="white", alpha=0.7)

        cm = plt.cm.viridis
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = bin_centers - min(bin_centers)
        col /= max(col)
        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))

        ax.set_xlabel("Score (%)", color="white", fontsize=12)
        ax.set_ylabel("Frequency", color="white", fontsize=12)
        ax.set_title("Score Distribution", color="white", fontsize=14)
        ax.tick_params(colors="white")
        ax.grid(True, alpha=0.3, axis='y')

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        tk.Button(frame, text="Back", command=self.show_performance_menu,
                  font=("Arial", 12), bg="#0f3460", fg="white",
                  width=15, height=2).pack(pady=10)

    def manage_questions(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        tk.Label(frame, text="Manage Questions", font=("Arial", 20, "bold"),
                 bg="#1a1a2e", fg="#00fff5").pack(pady=20)

        btn_frame = tk.Frame(frame, bg="#1a1a2e")
        btn_frame.pack(pady=20)

        btn_style = {"font": ("Arial", 12), "width": 20, "height": 2,
                     "bg": "#0f3460", "fg": "white"}

        tk.Button(btn_frame, text="Add Question", command=self.add_question, **btn_style).grid(row=0, column=0, padx=10,
                                                                                               pady=10)
        tk.Button(btn_frame, text="Edit Question", command=self.edit_question, **btn_style).grid(row=0, column=1,
                                                                                                 padx=10, pady=10)
        tk.Button(btn_frame, text="Delete Question", command=self.delete_question, **btn_style).grid(row=1, column=0,
                                                                                                     padx=10, pady=10)
        tk.Button(btn_frame, text="Back to Home", command=self.show_home_page, **btn_style).grid(row=1, column=1,
                                                                                                 padx=10, pady=10)

        filter_frame = tk.Frame(frame, bg="#1a1a2e")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filter by Subject:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(
            side="left", padx=5)

        subjects = ["All"] + self.db.get_subjects()
        self.subject_filter = tk.StringVar(value="All")
        subject_combo = ttk.Combobox(filter_frame, textvariable=self.subject_filter, values=subjects,
                                     state="readonly", font=("Arial", 11), width=15)
        subject_combo.pack(side="left", padx=5)
        subject_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_question_list())

        list_frame = tk.Frame(frame, bg="#1a1a2e")
        list_frame.pack(expand=True, fill="both", pady=20)

        tk.Label(list_frame, text="Current Questions:", font=("Arial", 14),
                 bg="#1a1a2e", fg="white").pack()

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.question_listbox = tk.Listbox(list_frame, font=("Arial", 11),
                                           bg="#0f3460", fg="white",
                                           yscrollcommand=scrollbar.set, height=15)
        self.question_listbox.pack(expand=True, fill="both", padx=10)
        scrollbar.config(command=self.question_listbox.yview)

        self.refresh_question_list()

    def refresh_question_list(self):
        self.question_listbox.delete(0, tk.END)

        filter_subject = self.subject_filter.get() if self.subject_filter else "All"

        if filter_subject == "All":
            questions = self.db.get_all_questions()
        else:
            questions = self.db.get_questions_by_subject(filter_subject)

        print(f"Refreshing list with {len(questions)} questions")

        for q in questions:
            self.question_listbox.insert(tk.END, f"[{q[1]}] ID:{q[0]} - {q[2][:50]}...")

    def add_question(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Question")
        add_window.geometry("550x600")
        add_window.configure(bg="#1a1a2e")

        tk.Label(add_window, text="Subject:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)

        existing_subjects = self.db.get_subjects()
        default_subjects = ["Python", "Java", "C", "C#"]
        all_subjects = list(set(existing_subjects + default_subjects))
        all_subjects.sort()

        subject_var = tk.StringVar(value=all_subjects[0] if all_subjects else "Python")
        subject_combo = ttk.Combobox(add_window, textvariable=subject_var, values=all_subjects,
                                     font=("Arial", 11), width=47)
        subject_combo.pack(pady=5)

        tk.Label(add_window, text="Question:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
        q_entry = tk.Text(add_window, height=3, width=50, font=("Arial", 11))
        q_entry.pack(pady=5)

        option_entries = []
        for i in range(4):
            tk.Label(add_window, text=f"Option {i + 1}:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
            entry = tk.Entry(add_window, width=50, font=("Arial", 11))
            entry.pack(pady=5)
            option_entries.append(entry)

        tk.Label(add_window, text="Correct Option (1-4):", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
        correct_entry = tk.Entry(add_window, width=10, font=("Arial", 11))
        correct_entry.pack(pady=5)

        def save_question():
            subject = subject_var.get().strip()
            question = q_entry.get("1.0", tk.END).strip()
            options = [entry.get().strip() for entry in option_entries]
            try:
                correct = int(correct_entry.get()) - 1
                if not subject or not question or any(not opt for opt in options):
                    messagebox.showerror("Error", "All fields are required")
                    return
                if correct < 0 or correct > 3:
                    messagebox.showerror("Error", "Correct option must be between 1-4")
                    return

                self.db.add_question(subject, question, options, correct)
                self.refresh_question_list()
                add_window.destroy()
                messagebox.showinfo("Success", "Question added successfully")
            except ValueError:
                messagebox.showerror("Error", "Invalid correct option number")

        tk.Button(add_window, text="Save", command=save_question,
                  font=("Arial", 12), bg="#0f3460", fg="white", width=15).pack(pady=20)

    def edit_question(self):
        selection = self.question_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a question to edit")
            return

        selected_text = self.question_listbox.get(selection[0])
        q_id = int(selected_text.split("ID:")[1].split(" - ")[0])

        filter_subject = self.subject_filter.get() if self.subject_filter else "All"
        if filter_subject == "All":
            questions = self.db.get_all_questions()
        else:
            questions = self.db.get_questions_by_subject(filter_subject)

        question_data = None
        for q in questions:
            if q[0] == q_id:
                question_data = q
                break

        if not question_data:
            messagebox.showerror("Error", "Question not found")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Question")
        edit_window.geometry("550x600")
        edit_window.configure(bg="#1a1a2e")

        tk.Label(edit_window, text="Subject:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)

        existing_subjects = self.db.get_subjects()
        default_subjects = ["Python", "Java", "C", "C#"]
        all_subjects = list(set(existing_subjects + default_subjects))
        all_subjects.sort()

        subject_var = tk.StringVar(value=question_data[1])
        subject_combo = ttk.Combobox(edit_window, textvariable=subject_var, values=all_subjects,
                                     font=("Arial", 11), width=47)
        subject_combo.pack(pady=5)

        tk.Label(edit_window, text="Question:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
        q_entry = tk.Text(edit_window, height=3, width=50, font=("Arial", 11))
        q_entry.insert("1.0", question_data[2])
        q_entry.pack(pady=5)

        option_entries = []
        for i in range(4):
            tk.Label(edit_window, text=f"Option {i + 1}:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
            entry = tk.Entry(edit_window, width=50, font=("Arial", 11))
            entry.insert(0, question_data[i + 3])
            entry.pack(pady=5)
            option_entries.append(entry)

        tk.Label(edit_window, text="Correct Option (1-4):", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
        correct_entry = tk.Entry(edit_window, width=10, font=("Arial", 11))
        correct_entry.insert(0, str(question_data[7]))
        correct_entry.pack(pady=5)

        def save_changes():
            subject = subject_var.get().strip()
            question = q_entry.get("1.0", tk.END).strip()
            options = [entry.get().strip() for entry in option_entries]
            try:
                correct = int(correct_entry.get()) - 1
                if not subject or not question or any(not opt for opt in options):
                    messagebox.showerror("Error", "All fields are required")
                    return
                if correct < 0 or correct > 3:
                    messagebox.showerror("Error", "Correct option must be between 1-4")
                    return

                self.db.update_question(question_data[0], subject, question, options, correct)
                self.refresh_question_list()
                edit_window.destroy()
                messagebox.showinfo("Success", "Question updated successfully")
            except ValueError:
                messagebox.showerror("Error", "Invalid correct option number")

        tk.Button(edit_window, text="Save Changes", command=save_changes,
                  font=("Arial", 12), bg="#0f3460", fg="white", width=15).pack(pady=20)

    def delete_question(self):
        selection = self.question_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a question to delete")
            return

        selected_text = self.question_listbox.get(selection[0])
        q_id = int(selected_text.split("ID:")[1].split(" - ")[0])

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this question?")

        if confirm:
            self.db.delete_question(q_id)
            self.refresh_question_list()
            messagebox.showinfo("Success", "Question deleted successfully")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()