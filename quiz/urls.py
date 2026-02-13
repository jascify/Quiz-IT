# quiz/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('choose-subject/', views.choose_subject_view, name='choose_subject'),
    path('quiz/<str:subject>/', views.quiz_view, name='quiz'),
    path('result/', views.result_view, name='result'),
    path('performance/', views.performance_menu_view, name='performance_menu'),
    path('my-scores/', views.my_scores_view, name='my_scores'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('distribution/', views.distribution_view, name='distribution'),
    path('manage-questions/', views.manage_questions_view, name='manage_questions'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
]