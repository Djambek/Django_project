"""В этом файле идет дополнение HTML кода"""
import urllib.parse
import time
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from bs4 import BeautifulSoup as bs
import requests
from .models import Book
from .models import Book_desc
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
        res = requests.get("https://litnet.com/ru/search?q=" + url+"&type=book")
        soup = bs(res.text, 'html.parser')
        book_name, href_book = [], []
        href = ''
        description = ''
        autors = []
        for a in soup.find_all("a", class_="author"):
            autors.append(a.text)

        for title_book in soup.find_all("h4", class_="book-title"):
            for name_book in title_book.find_all("a"):
                book_name.append(name_book.get_text())
                href_book.append("https://litnet.com" + name_book.get('href'))
        answer = []
        for link in href_book:
            res = requests.get(link)
            # href_book_answer = href_book[book_name.index(self.name_book)]
            soup = bs(res.text, 'html.parser')
            for div_main in soup.find_all("div", class_="col-md-12"):
                for div in div_main.find_all("div", class_="tab-pane active"):
                    description = div.text

            soup = bs(res.text, 'html.parser')
            for div_main in soup.find_all("div", class_="book-view_fx"):
                for div in div_main.find_all("div", class_="book-view-cover"):
                    for img in div.find_all("img"):
                        href = img.get("src")
            status_book = " Заморожена"
            if not soup.find_all("span", class_="book-status book-status-process"):
                status_book = " В процессе"
            if not soup.find_all("span", class_="book-status book-status-full"):
                status_book = " Завершена"
            answer.append([book_name[href_book.index(link)], status_book, href, link,  description, autors[href_book.index(link)]])
        return answer

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
        for name in names:
            href_book = ''
            for i in b_h:
                if name == i:
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
            answer = []
            for div in soup.find_all("div", class_="btn-price"):
                for span in div.find_all("span"):
                    answer.append([name, str(span.text).replace("  ", '').replace("\n", ""), href, href_book, description, autor])
            return answer

    def answer(self):
        litnet = self.book_in_litnet() if self.book_in_litnet()  is not  None else []
        litmarket = self.book_in_litmarket() if self.book_in_litmarket() is not None else []
        return litmarket+litnet


def books_list(request):
    username = User.objects.get(username=request.user.username)
    print(11)
    print(Book.objects.filter(people_book=username))
    ids = [i.book_id for i in Book.objects.filter(people_book=username)]
    books = []
    try:
        for id_ in ids:
            books.append(Book_desc.objects.filter(id=id_)[0])
            # names_book.append(Book_desc.objects.filter(id=id_)[0][0])
    except:
        pass
    status = {}
    for book in books:
        status[book.book_name] = book
        # print(BookStatus(i.book_name).answer()[0][0])
    return render(request, 'books/books_list.html', {'books': books, "status": status})



def desc(request, id_):
    b = Book_desc.objects.filter(id=id_)[0]
    return render(request, "books/b.html", {'book': b.book_name, "autor":b.book_autor, "status": b.book_status,"href_image": b.book_img_link, "href_site":b.book_link, "desc":b.book_desc})


def peoples(request):
    # num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    return render(request, "books/how_many.html", {"visit": num_visits})

def home(request):
    return render(request, "books/home.html")

def new_book(request):
    book_name = request.GET.get('book')
    print(book_name)
    book_ = BookStatus(book_name).answer()
    Book_desc.objects.create(book_name=book_[0][0],
                             book_autor=book_[0][5],
                             book_desc=book_[0][4],
                             book_link=book_[0][3],
                             book_status=book_[0][1],
                             book_img_link=book_[0][2])
    username = User.objects.get(username=request.user.username)
    Book.objects.create(
        book_id=Book_desc.objects.get(book_name=BookStatus(book_name).answer()[0][0]).id,
        people_book=username)
    print(1)
    return HttpResponseRedirect("/books_list")



def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form_new = BookForm(initial={"book_name": form["book_name"].value(), "book_autor": form["book_autor"].value()})

            if len(BookStatus(form["book_name"].value()).answer()) == 0:
                return render(request, 'books/add_book.html',{'form': form_new,
                                        "Not_book": "Ничего не найденно. Проверьте ошибки в написании"})
            elif len(BookStatus(form["book_name"].value()).answer()) > 1:
                return render(request, 'books/add_book.html', {'form': form_new,
                                                               "book_list":[i[0] for i in BookStatus(form["book_name"].value()).answer()],
                                                               "autors":[i[5] for i in BookStatus(form["book_name"].value()).answer()],
                                                               'range': range(len(BookStatus(form["book_name"].value()).answer()))})

            else:
                print(1)
                username = User.objects.get(username=request.user.username)
                print(len(Book_desc.objects.filter(book_name=form["book_name"].value())))
                if len(Book_desc.objects.filter(book_name=form["book_name"].value())) == 0:
                    print(333)
                    book = BookStatus(form["book_name"].value()).answer()
                    Book_desc.objects.create(book_name=book[0][0],
                                             book_autor=book[0][5],
                                             book_desc=book[0][4],
                                             book_link=book[0][3],
                                             book_status=book[0][1],
                                             book_img_link=book[0][2])
                print(2222)
                print("!!!")
                print(BookStatus(form["book_name"].value()).answer(), form["book_name"].value())
                # print(Book_desc.objects.filter(book_name=form["book_name"].value())[0].id)
                # print(Book_desc.objects.filter(book_name=BookStatus(form["book_name"].value()).answer()[0][0]
                Book.objects.create(book_id=Book_desc.objects.get(book_name=BookStatus(form["book_name"].value()).answer()[0][0]).id,
                                    people_book=username)
                return HttpResponseRedirect("/books_list")
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form,})

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
    username = User.objects.get(username=request.user.username)
    Book.objects.get(id=id_, people_book=username).delete()
    return render(request, "books/del.html")

def sure_del(request, id_):
    return render(request, "books/sure_del.html", {"book": Book.objects.get(book_id=id_)})

def profile(request):
    print(request.method)
    if request.method == "POST":
        form = Profile(request.POST)
        if form.is_valid():
            print(000)
            user_ = User.objects.get(username=request.user.username)
            print(user_)
            user_.username= form['username'].value()
            user_.email = form["email"].value()
            user_.save()
            return HttpResponseRedirect("/profile")
    else:
        print(22)
        form = Profile(initial={"username": request.user.username, "email": request.user.email})
    return render(request, 'books/profile.html', {'form': form})
if time.strftime("%H") == "01":
    books = Book.objects.all()
    for i in books:
        i.book_status = BookStatus(i.book_name).answer()[0][1]
        i.save()
        time.sleep(100)
