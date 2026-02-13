# quiz/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Score
from .forms import SignUpForm, LoginForm
import json
from datetime import datetime


def load_questions():
    try:
        with open('questions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_questions(questions):
    with open('questions.json', 'w') as f:
        json.dump(questions, f, indent=2)


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
    questions = load_questions()
    subjects = list(questions.keys())
    return render(request, 'quiz/choose_subject.html', {'subjects': subjects})


@login_required
def quiz_view(request, subject):
    questions = load_questions()

    if subject not in questions:
        messages.error(request, 'Subject not found')
        return redirect('choose_subject')

    if request.method == 'POST':
        subject_questions = questions[subject]
        score = 0
        total = len(subject_questions)

        for idx, question in enumerate(subject_questions):
            answer = request.POST.get(f'question_{idx}')
            if answer and int(answer) == question['correct']:
                score += 1

        percentage = (score / total * 100) if total > 0 else 0

        Score.objects.create(
            user=request.user,
            subject=subject,
            score=score,
            total=total,
            percentage=percentage
        )

        request.session['last_result'] = {
            'subject': subject,
            'score': score,
            'total': total,
            'percentage': percentage
        }

        return redirect('result')

    subject_questions = questions[subject]
    return render(request, 'quiz/quiz.html', {
        'subject': subject,
        'questions': subject_questions
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
    scores = Score.objects.filter(user=request.user).order_by('date')

    score_data = {
        'attempts': list(range(1, len(scores) + 1)),
        'percentages': [score.percentage for score in scores]
    }

    return render(request, 'quiz/my_scores.html', {
        'scores': scores,
        'score_data': json.dumps(score_data)
    })


@login_required
def leaderboard_view(request):
    all_scores = Score.objects.all()

    subject_scores = {}
    for score in all_scores:
        if score.subject not in subject_scores:
            subject_scores[score.subject] = []
        subject_scores[score.subject].append({
            'username': score.user.username,
            'percentage': score.percentage
        })

    for subject in subject_scores:
        subject_scores[subject] = sorted(subject_scores[subject], key=lambda x: x['percentage'], reverse=True)[:10]

    return render(request, 'quiz/leaderboard.html', {
        'subject_scores': json.dumps(subject_scores)
    })


@login_required
def distribution_view(request):
    all_scores = Score.objects.all()

    subject_data = {}
    for score in all_scores:
        if score.subject not in subject_data:
            subject_data[score.subject] = []
        subject_data[score.subject].append(score.percentage)

    return render(request, 'quiz/distribution.html', {
        'subject_data': json.dumps(subject_data)
    })


@login_required
def manage_questions_view(request):
    questions = load_questions()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            subject = request.POST.get('subject')
            question_text = request.POST.get('question')
            options = [
                request.POST.get('option1'),
                request.POST.get('option2'),
                request.POST.get('option3'),
                request.POST.get('option4')
            ]
            correct = int(request.POST.get('correct')) - 1

            if subject in questions:
                questions[subject].append({
                    'question': question_text,
                    'options': options,
                    'correct': correct
                })
                save_questions(questions)
                messages.success(request, 'Question added successfully!')

        elif action == 'delete':
            subject = request.POST.get('subject')
            index = int(request.POST.get('index'))

            if subject in questions and 0 <= index < len(questions[subject]):
                del questions[subject][index]
                save_questions(questions)
                messages.success(request, 'Question deleted successfully!')

        return redirect('manage_questions')

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

    for user in users:
        scores = Score.objects.filter(user=user)
        total_attempts = scores.count()
        avg_score = sum(s.percentage for s in scores) / total_attempts if total_attempts > 0 else 0

        user_data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'total_attempts': total_attempts,
            'avg_score': avg_score
        })

    return render(request, 'quiz/manage_users.html', {'users': user_data})