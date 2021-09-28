"""Форма для смены ника или почты"""
from django import forms
from django.contrib.auth.models import User
class Profile(forms.Form):
    username = forms.CharField(max_length=200)
    email = forms.CharField(max_length=200)

