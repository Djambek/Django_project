"""Форма для смены ника или почты"""
from django import forms
from django.contrib.auth.models import User
class Profile(forms.ModelForm):
    """В этом классе описывается форма"""
    class Meta:
        model = User
        fields = ('username', 'email')
