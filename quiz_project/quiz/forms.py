# quiz/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your full name'
    }))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Choose a username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Create a password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = User
        fields = ('first_name', 'username', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your password'
    }))