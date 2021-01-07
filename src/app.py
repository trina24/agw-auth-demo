from falcon import API

from src.resources import Book, BookList

app = API()

app.add_route('/books/{id}', Book())
app.add_route('/books', BookList())
