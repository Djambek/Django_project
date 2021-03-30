"""В этом файле идет дополнение HTML кода"""
import urllib.parse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from bs4 import BeautifulSoup as bs
import requests
from .models import Book
from .form_book import BookForm
from .form_profile import Profile
from .forms import SignUpForm

class BookStatus():
    def __init__(self, name_book):
        self.name_book = name_book

    def book_in_litnet(self):
        url = urllib.parse.quote_plus(self.name_book)
        res = requests.get("https://litnet.com/ru/search?q=" + url)
        soup = bs(res.text, 'html.parser')
        book_name, href_book = [], []
        status_book = ""
        for title_book in soup.find_all("h4", class_="book-title"):
            for name_book in title_book.find_all("a"):
                book_name.append(name_book.get_text())
                href_book.append("https://litnet.com/" + name_book.get('href'))
        for status in soup.find_all("span", class_="book-status book-status-process"):
            status_book = str(status.get_text().strip().split(":")[0])
        if len(book_name) > 1:
            return "Слишком много вариантов"
        if len(book_name) == 0:
            return "Ничего не найденно"
        if status_book != '':
            return status_book[26:]

    def number_of_pages(self):
        return self


def books_list(request):
    username= User.objects.get(username=request.user.username)
    books = Book.objects.filter(people_book=username).order_by('published_date')
    status = {}
    for i in books:
        status[i.book_name] = BookStatus(i.book_name).book_in_litnet()
    return render(request, 'books/books_list.html', {'books': books, "status": status, })



def desc(request, id_):
    book = Book.objects.filter(id=id_)
    status = BookStatus(str(book[0].book_name)).book_in_litnet()

    return render(request, "books/b.html", {'book': book[0], "status": status})


def peoples(request):
    # num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    return render(request, "books/how_many.html", {"visit": num_visits})

def home(request):
    return render(request, "books/home.html")

def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            username = User.objects.get(username=request.user.username)
            Book.objects.create(book_name=form["book_name"].value(),
                                autor_book=form["autor_book"].value(),
                                people_book=username)
            return HttpResponseRedirect("/books_list")
    else:

        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            user = authenticate(username=username, password=raw_password, email=email)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'books/signup.html', {'form': form})
def del_(request, id_):
    Book.objects.get(id=id_).delete()
    return render(request, "books/del.html")
def sure_del(request, id_):
    return render(request, "books/sure_del.html", {"book":Book.objects.get(id=id_)})

def book_edit(request, id_):
    username = User.objects.get(username=request.user.username)
    book = Book.objects.filter(id=id_, people_book=username)[0]
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            # book = form.save(commit=False)
            book.autor_book = form["autor_book"].value()
            book.book_name = form["book_name"].value()
            book.published_date = timezone.now()
            book.people_book = username
            book.save()
            return HttpResponseRedirect("/"+str(id)+'/desc')
    else:
        form = BookForm(initial={"book_name": book.book_name, "autor_book": book.autor_book})
    return render(request, 'books/book_edit.html', {'form': form})

def pofile(request):
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = Profile(request.POST)
        if form.is_valid():
            user.username= form['username'].value()
            user.email = form["email"].value()
            user.save()
            return HttpResponseRedirect("/profile")
    else:
        form = Profile(initial={"username": user.username, "email": user.email})
    return render(request, 'books/profile.html', {'form': form})
