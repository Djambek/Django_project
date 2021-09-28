"Администрирование"
from django.contrib import admin
from .models import Book
from .models import Book_desc
admin.site.register(Book)
admin.site.register(Book_desc)
