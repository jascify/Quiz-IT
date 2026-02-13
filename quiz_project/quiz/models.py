# quiz/models.py
from django.db import models
from django.contrib.auth.models import User
import json

# Base Model Class - Demonstrates Inheritance and Encapsulation
class BaseModel(models.Model):
    """Abstract base model with common fields - Encapsulation"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def to_dict(self):
        """Convert model to dictionary - Polymorphism (can be overridden)"""
        return {
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Score(BaseModel):
    """Score model - Demonstrates Inheritance from BaseModel"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    
    # Private field for metadata - Encapsulation
    _metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.percentage}%"
    
    # Override parent method - Polymorphism
    def to_dict(self):
        """Convert score to dictionary with additional fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'username': self.user.username,
            'subject': self.subject,
            'score': self.score,
            'total': self.total,
            'percentage': self.percentage
        })
        return base_dict
    
    def get_grade(self):
        """Calculate grade based on percentage - Encapsulation"""
        # Using Lambda expressions in array
        grade_ranges = [
            (lambda p: p >= 90, 'A+'),
            (lambda p: p >= 80, 'A'),
            (lambda p: p >= 70, 'B'),
            (lambda p: p >= 60, 'C'),
            (lambda p: p >= 50, 'D'),
            (lambda p: True, 'F')
        ]
        
        # Loop through array of tuples
        for condition, grade in grade_ranges:
            if condition(self.percentage):
                return grade
        return 'F'
    
    def save_metadata(self, key, value):
        """Private metadata setter - Encapsulation"""
        self._metadata[key] = value
        self.save()
    
    def get_metadata(self, key):
        """Private metadata getter - Encapsulation"""
        return self._metadata.get(key)


class Question(BaseModel):
    """Question model storing in JSON format"""
    subject = models.CharField(max_length=100)
    question_text = models.TextField()
    options = models.JSONField()  # Array stored as JSON
    correct_answer = models.IntegerField()
    difficulty = models.CharField(max_length=20, default='medium')
    
    def __str__(self):
        return f"{self.subject}: {self.question_text[:50]}"
    
    # Polymorphism - Override parent method
    def to_dict(self):
        """Convert question to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'subject': self.subject,
            'question': self.question_text,
            'options': self.options,
            'correct': self.correct_answer,
            'difficulty': self.difficulty
        })
        return base_dict