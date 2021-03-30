"""Эта форма для добавления книг"""
from django import forms

from .models import Book

class BookForm(forms.ModelForm):
    """В этом классе описывается форма"""
    class Meta:
        model = Book
        fields = ('book_name', 'autor_book')
