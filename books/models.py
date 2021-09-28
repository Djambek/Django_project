"""В этом файле создается модель нашего приложения"""
from django.db import models
from django.conf import settings

class Book(models.Model):
    """В этом классе описываются какую информацию мы будем хранить о книгах"""
    people_book = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=3000)

class Book_desc(models.Model):
    book_name = models.CharField(max_length=3000)
    book_autor = models.CharField(max_length=3000)
    book_desc = models.CharField(max_length=30000)
    book_link = models.CharField(max_length=3000)
    book_status = models.CharField(max_length=3000)
    book_img_link = models.CharField(max_length=3000)

