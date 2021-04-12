from bs4 import BeautifulSoup as bs
import requests
import urllib.parse
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

book = BookStatus("Последняя петля ")
print(book.answer())
