"""В этом файле создается модель нашего приложения"""
from django.db import models
from django.conf import settings

class Book(models.Model):
    """В этом классе описываются какую информацию мы будем хранить о книгах"""
    autor_book = models.CharField(max_length=300)
    book_name = models.CharField(max_length=300)
    published_date = models.DateTimeField(blank=True, null=True)
    people_book = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # book_status = status(book_name) # статутс книги - в процессе или уже готова
    # book_desctiption = models.CharField(max_length=3000) # описание, если оно конечно будет
    # book_image = ImageField(upload_to='templates') # тут будут хранится картинки обложнки
    # book_href = models.CharField(max_length=1000) # тут будет ссылка на книгу
