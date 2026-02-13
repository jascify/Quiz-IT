# quiz/models.py
from django.db import models
from django.contrib.auth.models import User

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.percentage}%"