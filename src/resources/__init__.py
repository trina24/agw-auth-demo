import json
from functools import wraps
from typing import Callable, Dict, List, Union

from falcon import HTTP_200, HTTP_201, HTTP_404, Request, Response

from src.exceptions import ResourceNotFound
from src.models import BookModel


def serialize(response: Union[BookModel, List[BookModel]]) -> str:
    if isinstance(response, List):
        return json.dumps(list(map(lambda x: x.serialized, response)))
    else:
        return json.dumps(response.serialized)


def not_found_wrapper(function: Callable) -> Callable:
    @wraps(function)
    def decorated_function(self, req, resp, id) -> None:
        try:
            function(self, req, resp, id)
        except ResourceNotFound:
            resp.body = json.dumps({'message': 'Book doesn\'t exist'})
            resp.status = HTTP_404
    return decorated_function


class BookList:

    @classmethod
    def add_one(cls, body: Dict) -> BookModel:
        book = BookModel(**body)
        book.save()
        return book

    @classmethod
    def add_many(cls, payload: List[Dict]) -> List[BookModel]:
        books = list(map(lambda x: BookModel(**x), payload))
        return BookModel.save_many(books)

    def on_post(self, req: Request, resp: Response) -> None:
        body = req.media
        if isinstance(body, List):
            resp.body = serialize(self.add_many(body))
        else:
            resp.body = serialize(self.add_one(body))
        resp.status = HTTP_201

    def on_get(self, req: Request, resp: Response) -> None:
        author = req.params.get('author')
        if author is not None:
            resp.body = serialize(BookModel.get_by_author(req.params['author']))
        else:
            resp.body = serialize(BookModel.get_all())
        resp.status = HTTP_200


class Book:

    @not_found_wrapper
    def on_delete(self, req: Request, resp: Response, id: str) -> None:
        book = BookModel.get_by_id(id)
        book.delete()
        resp.body = serialize(book)
        resp.status = HTTP_200

    @not_found_wrapper
    def on_get(self, req: Request, resp: Response, id: str) -> None:
        resp.body = serialize(BookModel.get_by_id(id))
        resp.status = HTTP_200
