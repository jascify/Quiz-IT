# quiz/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Score, Question
from .forms import SignUpForm, LoginForm
import json
import os
from django.conf import settings
from datetime import datetime


# ============= INHERITANCE: Base Class =============
class DataManager:
    """Base class for managing data - Demonstrates Encapsulation and Inheritance"""
    
    def __init__(self):
        self._data = []  # Private variable - Encapsulation
        self._file_path = None
    
    def _load_data(self):
        """Private method - Encapsulation"""
        raise NotImplementedError("Subclasses must implement _load_data")
    
    def get_data(self):
        """Public getter method - Encapsulation"""
        return self._data
    
    def set_data(self, data):
        """Public setter method - Encapsulation"""
        self._data = data
    
    def filter_data(self, condition):
        """Filter data using lambda - Demonstrates Lambda expressions"""
        return list(filter(condition, self._data))
    
    def map_data(self, transform):
        """Map data using lambda - Demonstrates Lambda expressions"""
        return list(map(transform, self._data))


# ============= INHERITANCE: Derived Class 1 =============
class QuestionManager(DataManager):
    """Manages questions from JSON file - Demonstrates Inheritance"""
    
    def __init__(self):
        super().__init__()  # Call parent constructor
        self._file_path = os.path.join(settings.BASE_DIR, 'questions.json')
        self._data = self._load_data()
    
    # Override parent method - Polymorphism
    def _load_data(self):
        """Load questions from JSON file - JSON usage"""
        try:
            with open(self._file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return self._create_default_questions()
                return json.loads(content)  # JSON parsing
        except (FileNotFoundError, json.JSONDecodeError):
            return self._create_default_questions()
    
    def _create_default_questions(self):
        """Create default questions - Arrays and JSON"""
        default_questions = {
            "Python": [
                {
                    "question": "What is Polymorphism in Python?",
                    "options": [
                        "The ability of different objects to respond to the same method call",
                        "Creating multiple classes",
                        "Using multiple inheritance",
                        "Defining private variables"
                    ],
                    "correct": 0
                },
                {
                    "question": "Which keyword is used for Inheritance in Python?",
                    "options": [
                        "extends",
                        "inherits",
                        "class ChildClass(ParentClass):",
                        "implements"
                    ],
                    "correct": 2
                },
                {
                    "question": "What does Encapsulation mean in Python?",
                    "options": [
                        "Hiding implementation details using private variables",
                        "Creating multiple classes",
                        "Using loops",
                        "Creating functions"
                    ],
                    "correct": 0
                },
                {
                    "question": "How do you create a private variable in Python?",
                    "options": [
                        "private var_name",
                        "_var_name or __var_name",
                        "#var_name",
                        "var_name (private)"
                    ],
                    "correct": 1
                },
                {
                    "question": "What is the correct syntax for a lambda function in Python?",
                    "options": [
                        "lambda x: x + 1",
                        "def lambda(x): return x + 1",
                        "lambda(x) => x + 1",
                        "x => x + 1"
                    ],
                    "correct": 0
                }
            ],
            "Java": [
                {
                    "question": "Which keyword is used for Inheritance in Java?",
                    "options": [
                        "implements",
                        "extends",
                        "inherits",
                        "derive"
                    ],
                    "correct": 1
                },
                {
                    "question": "What is Polymorphism in Java?",
                    "options": [
                        "Multiple forms of a single entity",
                        "Creating multiple classes",
                        "Using interfaces",
                        "Method overriding only"
                    ],
                    "correct": 0
                },
                {
                    "question": "Which access modifier provides Encapsulation in Java?",
                    "options": [
                        "public",
                        "private",
                        "protected",
                        "default"
                    ],
                    "correct": 1
                }
            ],
            "C": [
                {
                    "question": "How do you declare an array in C?",
                    "options": [
                        "int arr[5];",
                        "array int arr = 5;",
                        "int[] arr = new int[5];",
                        "arr = int[5];"
                    ],
                    "correct": 0
                },
                {
                    "question": "Which loop checks condition at the end?",
                    "options": [
                        "for loop",
                        "while loop",
                        "do-while loop",
                        "foreach loop"
                    ],
                    "correct": 2
                }
            ],
            "C#": [
                {
                    "question": "Which keyword is used for Inheritance in C#?",
                    "options": [
                        "extends",
                        ":",
                        "inherits",
                        "implements"
                    ],
                    "correct": 1
                },
                {
                    "question": "What is Polymorphism in C#?",
                    "options": [
                        "Ability to take many forms",
                        "Creating classes",
                        "Using namespaces",
                        "Defining variables"
                    ],
                    "correct": 0
                }
            ]
        }
        
        # Save to JSON file
        with open(self._file_path, 'w') as f:
            json.dump(default_questions, f, indent=2)
        
        return default_questions
    
    def save_questions(self):
        """Save questions to JSON file"""
        with open(self._file_path, 'w') as f:
            json.dump(self._data, f, indent=2)
    
    def get_subjects(self):
        """Get list of subjects - Array operation"""
        return list(self._data.keys())
    
    def get_questions_by_subject(self, subject):
        """Get questions for a specific subject"""
        return self._data.get(subject, [])
    
    def add_question(self, subject, question_data):
        """Add a new question"""
        if subject in self._data:
            self._data[subject].append(question_data)
            self.save_questions()
    
    def delete_question(self, subject, index):
        """Delete a question by index"""
        if subject in self._data and 0 <= index < len(self._data[subject]):
            del self._data[subject][index]
            self.save_questions()


# ============= INHERITANCE: Derived Class 2 =============
class ScoreManager(DataManager):
    """Manages scores from database - Demonstrates Inheritance and Polymorphism"""
    
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self._data = self._load_data()
    
    # Override parent method - Polymorphism
    def _load_data(self):
        """Load scores from MySQL database"""
        if self.user:
            return list(Score.objects.filter(user=self.user))
        return list(Score.objects.all())
    
    def get_statistics(self):
        """Calculate statistics using lambda expressions and arrays"""
        if not self._data:
            return {
                'total_attempts': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            }
        
        # Using lambda expressions with map
        percentages = self.map_data(lambda score: score.percentage)
        
        return {
            'total_attempts': len(self._data),
            'average_score': sum(percentages) / len(percentages),
            'highest_score': max(percentages),
            'lowest_score': min(percentages)
        }
    
    def get_scores_above_threshold(self, threshold):
        """Get scores above threshold using lambda - Demonstrates Lambda"""
        return self.filter_data(lambda score: score.percentage >= threshold)
    
    def group_by_subject(self):
        """Group scores by subject - Array operations"""
        grouped = {}
        # Loop through array
        for score in self._data:
            if score.subject not in grouped:
                grouped[score.subject] = []
            grouped[score.subject].append(score)
        return grouped


# ============= POLYMORPHISM: Score Calculator Classes =============
class ScoreCalculator:
    """Base calculator class - Demonstrates Polymorphism"""
    
    def __init__(self, total_questions):
        self._total = total_questions
        self._correct = 0
        self._answers = []  # Array to store answers
    
    def add_answer(self, is_correct):
        """Add answer to array"""
        self._answers.append(is_correct)
        if is_correct:
            self._correct += 1
    
    def calculate_percentage(self):
        """Calculate percentage - Can be overridden"""
        if self._total == 0:
            return 0
        return (self._correct / self._total) * 100
    
    def get_score(self):
        """Get raw score"""
        return self._correct
    
    def get_total(self):
        """Get total questions"""
        return self._total
    
    def get_remark(self):
        """Get remark - Polymorphism (can be overridden in child classes)"""
        percentage = self.calculate_percentage()
        
        # Lambda expressions in array of tuples
        remarks = [
            (lambda p: p >= 90, "Outstanding! 🌟", "#5BC0BE"),
            (lambda p: p >= 80, "Excellent! 🎉", "#5BC0BE"),
            (lambda p: p >= 70, "Very Good! 👏", "#5BC0BE"),
            (lambda p: p >= 60, "Good Job! 👍", "#5BC0BE"),
            (lambda p: p >= 50, "Keep Trying! 💪", "#3A506B"),
            (lambda p: True, "Practice More! 📚", "#3A506B")
        ]
        
        # Loop through array
        for condition, remark, color in remarks:
            if condition(percentage):
                return remark, color
        
        return "Keep Practicing! 📚", "#3A506B"


class DetailedScoreCalculator(ScoreCalculator):
    """Extended calculator with detailed analysis - Demonstrates Inheritance"""
    
    def __init__(self, total_questions):
        super().__init__(total_questions)
        self._time_taken = []  # Array to store time for each question
    
    def add_answer_with_time(self, is_correct, time_seconds):
        """Add answer with time - Method extension"""
        self.add_answer(is_correct)
        self._time_taken.append(time_seconds)
    
    # Override parent method - Polymorphism
    def get_remark(self):
        """Get detailed remark with time analysis"""
        base_remark, color = super().get_remark()
        
        if self._time_taken:
            avg_time = sum(self._time_taken) / len(self._time_taken)
            time_comment = f" (Avg time: {avg_time:.1f}s per question)"
            return base_remark + time_comment, color
        
        return base_remark, color
    
    def get_detailed_stats(self):
        """Get detailed statistics using lambda and arrays"""
        if not self._time_taken:
            return {}
        
        return {
            'total_time': sum(self._time_taken),
            'avg_time': sum(self._time_taken) / len(self._time_taken),
            'fastest': min(self._time_taken),
            'slowest': max(self._time_taken)
        }


# Global instances
question_manager = QuestionManager()


# ============= VIEW FUNCTIONS =============
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'quiz/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'quiz/signup.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'quiz/home.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def choose_subject_view(request):
    subjects = question_manager.get_subjects()  # Array operation
    return render(request, 'quiz/choose_subject.html', {'subjects': subjects})


@login_required
def quiz_view(request, subject):
    questions = question_manager.get_questions_by_subject(subject)
    
    if not questions:
        messages.error(request, 'Subject not found')
        return redirect('choose_subject')
    
    if request.method == 'POST':
        # Create calculator instance
        calculator = ScoreCalculator(len(questions))
        
        # Loop through questions array
        for idx, question in enumerate(questions):
            answer = request.POST.get(f'question_{idx}')
            is_correct = answer and int(answer) == question['correct']
            calculator.add_answer(is_correct)
        
        # Calculate results
        score = calculator.get_score()
        total = calculator.get_total()
        percentage = calculator.calculate_percentage()
        remark, color = calculator.get_remark()
        
        # Save to MySQL database
        Score.objects.create(
            user=request.user,
            subject=subject,
            score=score,
            total=total,
            percentage=percentage
        )
        
        # Store in session as JSON
        request.session['last_result'] = {
            'subject': subject,
            'score': score,
            'total': total,
            'percentage': percentage,
            'remark': remark,
            'color': color
        }
        
        return redirect('result')
    
    return render(request, 'quiz/quiz.html', {
        'subject': subject,
        'questions': questions
    })


@login_required
def result_view(request):
    result = request.session.get('last_result')
    if not result:
        return redirect('home')
    
    return render(request, 'quiz/result.html', {'result': result})


@login_required
def performance_menu_view(request):
    return render(request, 'quiz/performance_menu.html')


@login_required
def my_scores_view(request):
    # Use ScoreManager to get scores
    score_manager = ScoreManager(user=request.user)
    scores = score_manager.get_data()
    
    # Get statistics using lambda
    stats = score_manager.get_statistics()
    
    # Array operations with list comprehension (similar to lambda)
    score_data = {
        'attempts': [i + 1 for i in range(len(scores))],  # Array generation
        'percentages': [score.percentage for score in scores],  # Array mapping
        'subjects': [score.subject for score in scores]  # Array extraction
    }
    
    return render(request, 'quiz/my_scores.html', {
        'scores': scores,
        'score_data': json.dumps(score_data),  # JSON serialization
        'stats': stats
    })


@login_required
def leaderboard_view(request):
    # Get all scores from database
    all_scores = Score.objects.all()
    
    # Group by subject using dictionary (like a hash map)
    subject_scores = {}
    
    # Loop through scores array
    for score in all_scores:
        if score.subject not in subject_scores:
            subject_scores[score.subject] = []
        subject_scores[score.subject].append({
            'username': score.user.username,
            'percentage': score.percentage
        })
    
    # Sort using lambda expression
    for subject in subject_scores:
        subject_scores[subject] = sorted(
            subject_scores[subject],
            key=lambda x: x['percentage'],  # Lambda for sorting
            reverse=True
        )[:10]  # Array slicing - get top 10
    
    return render(request, 'quiz/leaderboard.html', {
        'subject_scores': json.dumps(subject_scores)  # JSON serialization
    })


@login_required
def distribution_view(request):
    all_scores = Score.objects.all()
    
    subject_data = {}
    
    # Loop to organize data
    for score in all_scores:
        if score.subject not in subject_data:
            subject_data[score.subject] = []
        subject_data[score.subject].append(score.percentage)
    
    # Calculate statistics for each subject using lambda
    subject_stats = {}
    for subject, percentages in subject_data.items():
        subject_stats[subject] = {
            'data': percentages,
            'count': len(percentages),
            'average': sum(percentages) / len(percentages) if percentages else 0,
            'max': max(percentages) if percentages else 0,
            'min': min(percentages) if percentages else 0
        }
    
    return render(request, 'quiz/distribution.html', {
        'subject_data': json.dumps(subject_data),
        'subject_stats': json.dumps(subject_stats)
    })


@login_required
def manage_questions_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            subject = request.POST.get('subject')
            question_text = request.POST.get('question')
            
            # Array of options
            options = [
                request.POST.get('option1'),
                request.POST.get('option2'),
                request.POST.get('option3'),
                request.POST.get('option4')
            ]
            
            # Filter empty options using lambda
            options = list(filter(lambda x: x and x.strip(), options))
            
            correct = int(request.POST.get('correct')) - 1
            
            # Create question dictionary (JSON structure)
            question_data = {
                'question': question_text,
                'options': options,
                'correct': correct
            }
            
            question_manager.add_question(subject, question_data)
            messages.success(request, 'Question added successfully!')
            
        elif action == 'delete':
            subject = request.POST.get('subject')
            index = int(request.POST.get('index'))
            question_manager.delete_question(subject, index)
            messages.success(request, 'Question deleted successfully!')
        
        return redirect('manage_questions')
    
    questions = question_manager.get_data()
    return render(request, 'quiz/manage_questions.html', {'questions': questions})


@login_required
def manage_users_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_user':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            
            if user != request.user:
                user.delete()
                messages.success(request, f'User {user.username} deleted successfully!')
            else:
                messages.error(request, 'You cannot delete your own account!')
        
        elif action == 'clear_scores':
            user_id = request.POST.get('user_id')
            Score.objects.filter(user_id=user_id).delete()
            messages.success(request, 'User scores cleared successfully!')
        
        elif action == 'reset_all':
            Score.objects.all().delete()
            messages.success(request, 'All scores reset successfully!')
        
        return redirect('manage_users')
    
    users = User.objects.all()
    user_data = []
    
    # Loop through users
    for user in users:
        scores = Score.objects.filter(user=user)
        total_attempts = scores.count()
        
        # Using lambda to calculate average
        percentages = list(map(lambda s: s.percentage, scores))
        avg_score = sum(percentages) / len(percentages) if percentages else 0
        
        # Using lambda to filter high scores
        high_scores = list(filter(lambda p: p >= 80, percentages))
        
        user_data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'total_attempts': total_attempts,
            'avg_score': avg_score,
            'high_score_count': len(high_scores)
        })
    
    # Sort users by average score using lambda
    user_data = sorted(user_data, key=lambda u: u['avg_score'], reverse=True)
    
    return render(request, 'quiz/manage_users.html', {'users': user_data})


