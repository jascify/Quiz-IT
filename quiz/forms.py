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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password2', 'Passwords do not match.')
            else:
                if len(password) < 8:
                    self.add_error('password1', 'Password must be at least 8 characters long.')
                if not any(char.isupper() for char in password):
                    self.add_error('password1', 'Password must contain at least one uppercase letter.')
                if not any(char.islower() for char in password):
                    self.add_error('password1', 'Password must contain at least one lowercase letter.')
                if not any(char.isdigit() or not char.isalnum() for char in password):
                    self.add_error('password1', 'Password must contain at least one number or special character.')
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your password'
    }))