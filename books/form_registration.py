"""Форма для регистрации нового пользователя"""
from django import forms
from .models import User
class UserRegistrationForm(forms.ModelForm):
    """В классе описывается форма регистрации нового пользователя"""
    class Meta:
        model = User
        fields = ('username', 'email', "password")
        widgets = {
            'password': forms.PasswordInput(),
        }
