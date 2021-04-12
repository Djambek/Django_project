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
def get_key(dic, value):
    for k, val in dic.items():
        if val == value:
            return k
class BookStatus():
    def __init__(self, name_book):
        self.name_book = name_book

    def book_in_litnet(self):
        url = urllib.parse.quote_plus(self.name_book)
        res = requests.get("https://litnet.com/ru/search?q=" + url)
        soup = bs(res.text, 'html.parser')
        book_name, href_book = [], []
        status_book = " Заморожена"
        href = ''
        description = ''
        autors = []
        for a in soup.find_all("a", class_="author"):
            autors.append(a.text)

        for title_book in soup.find_all("h4", class_="book-title"):
            for name_book in title_book.find_all("a"):
                book_name.append(name_book.get_text())
                href_book.append("https://litnet.com" + name_book.get('href')+"&type=book")


        if not soup.find_all("span", class_="book-status book-status-process"):
            status_book = " В процессе"
        if not soup.find_all("span", class_="book-status book-status-full"):
            status_book = " Завершена"
        if len(book_name) > 1:
            return book_name, autors
        if len(book_name) == 0:
            return None

        try:
            autor = ''
            href_book_answer = ''
            res = requests.get(href_book[book_name.index(self.name_book)])
            href_book_answer = href_book[book_name.index(self.name_book)]
            soup = bs(res.text, 'html.parser')
            for div_main in soup.find_all("div", class_="col-md-12"):
                for div in div_main.find_all("div", class_="tab-pane active"):
                    description = div.text
            for a in soup.find_all("a", class_="author"):
                autor = a.text
        except:
            return None
        soup = bs(res.text, 'html.parser')
        for div_main in soup.find_all("div", class_="book-view_fx"):
            for div in div_main.find_all("div", class_="book-view-cover"):
                for img in div.find_all("img"):
                    href = img.get("src")
        if href_book_answer != '':
            return status_book,  href, href_book_answer, description, autor
        return None
    def book_in_litmarket(self):
        b_h = {}
        url = urllib.parse.quote_plus(self.name_book)
        res = requests.get("https://litmarket.ru/search?query=" + url + "&type=book")
        soup = bs(res.text, 'html.parser')
        names = []
        autors = []
        for div in  soup.find_all("div", class_="card-author"):
            for a in div.find_all("a"):
                autors.append(a.text)
        for div in soup.find_all("div", class_="card-name"):
            for a in div.find_all("a"):
                b_h[a.text] = a.get("href")
        autors_answer = []
        for i in range(len(b_h)):
            if  self.name_book in list(b_h.keys())[i] :
                names.append(list(b_h.keys())[i])
                autors_answer.append(autors[i])
        if len(names) == 1:
            href_book = ''
            for i in b_h:
                if names[0] == i:
                    href_book = b_h[i]
            res = requests.get(href_book)
            soup = bs(res.text, 'html.parser')
            href = ""
            for a in soup.find_all("a", class_="cover-modal-link"):
                for img in a.find_all("img"):
                    href = img["data-src"]
            description = ''
            autor = ''
            for div in soup.find_all("div", class_="card-author"):
                for a in div.find_all("a"):
                    autor = a.text
            for div in soup.find_all("div", class_="card-description"):
                description = div.text

            for div in soup.find_all("div", class_="btn-price"):
                for span in div.find_all("span"):
                    return str(span.text).replace("  ", '').replace("\n", ""), href, href_book, description, autor

        elif len(names) == 0:
            return None
        else:
            return names, autors_answer

    def answer(self):
        litnet = self.book_in_litnet()
        litmarket = self.book_in_litmarket()
        if litnet is not None:
            try:
                if (isinstance(litnet[0], list) and isinstance(litmarket[0], list)):
                    return litnet[0]+litmarket[0], litnet[1]+litmarket[1]
                elif isinstance(litnet[0], str):
                    return litnet
                elif isinstance(litmarket[0], str):
                    return litmarket
            except:
                if litnet is None:
                    return litmarket
                return litnet
        elif litmarket is not None:
            return litmarket
        else:
            return None



def books_list(request):
    username= User.objects.get(username=request.user.username)
    books = Book.objects.filter(people_book=username).order_by('published_date')
    status = {}
    for i in books:
        status[i.book_name] = BookStatus(i.book_name).answer()[0]
    return render(request, 'books/books_list.html', {'books': books, "status": status})



def desc(request, id_):
    book = Book.objects.filter(id=id_)
    status, href_image, href_site, desc, autor = BookStatus(str(book[0].book_name)).answer()

    return render(request, "books/b.html", {'book': book[0], "status": status,"href_image": href_image, "href_site":href_site, "desc":desc})


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
            print(BookStatus(form["book_name"].value()).answer()[1])
            form_new = BookForm(initial={"book_name": form["book_name"].value(), "autor_book": form["autor_book"].value()})
            if isinstance(BookStatus(form["book_name"].value()).answer()[1], list):
                return render(request, 'books/add_book.html', {'form': form_new,
                                                               "book_list":BookStatus(form["book_name"].value()).answer()[0],
                                                               "autors":BookStatus(form["book_name"].value()).answer()[1],
                                                               'range': range(len(BookStatus(form["book_name"].value()).answer()[0]))})
            elif BookStatus(form["book_name"].value()).answer() is None:
                return render(request, 'books/add_book.html',{'form': form_new,
                                        "Not_book": "Ничего не найденно. Проверьте ошибки в написании"})
            else:
                print(1)
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
