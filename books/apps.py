"В этом файле указываем название нашего приложения"
from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Именно в этом классе это происходит"""
    name = 'books'
