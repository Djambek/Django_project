"""Эта форма для добавления книг"""
from django import forms

from .models import Book_desc

class BookForm(forms.ModelForm):
    """В этом классе описывается форма"""
    class Meta:
        model = Book_desc
        fields = ('book_name', 'book_autor')
