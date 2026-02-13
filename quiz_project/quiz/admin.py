# quiz/admin.py
from django.contrib import admin
from .models import Score, Question

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'score', 'total', 'percentage', 'date']
    list_filter = ['subject', 'date']
    search_fields = ['user__username', 'subject']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'question_text', 'difficulty', 'created_at']
    list_filter = ['subject', 'difficulty']
    search_fields = ['question_text']