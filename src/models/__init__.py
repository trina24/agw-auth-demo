from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
from numbers import Number
from typing import Dict, List, Union
from uuid import UUID, uuid4

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model

from src.config import AWS_REGION, TABLE_NAME
from src.exceptions import ResourceNotFound


class AuthorIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'author-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    author = UnicodeAttribute(hash_key=True)


class BookItem(Model):

    class Meta:
        table_name = TABLE_NAME
        region = AWS_REGION

    id = UnicodeAttribute(hash_key=True)
    created_at = UnicodeAttribute(range_key=True)
    author = UnicodeAttribute()
    title = UnicodeAttribute()
    year = NumberAttribute()
    author_index = AuthorIndex()


class BookModelFrame:

    batch_write = BookItem.batch_write


@dataclass
class BookModel(BookModelFrame):

    author: str
    title: str
    year: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._db = BookItem(**self.serialized)

    @classmethod
    def _load(cls, book: BookItem) -> BookModel:
        book_dict = book.attribute_values
        book_dict['id'] = UUID(book_dict['id'])
        book_dict['created_at'] = datetime.strptime(book_dict['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        return cls(**book_dict)

    @property
    def serialized(self) -> Dict:
        book_dict = asdict(self)
        for key, value in book_dict.items():
            if not isinstance(value, Number):
                book_dict[key] = str(value)
        return book_dict

    def save(self) -> None:
        self._db.save()

    @classmethod
    def save_many(cls, books: List[BookModel]) -> List[BookModel]:
        with cls.batch_write() as batch:
            for book in books:
                batch.save(book._db)
        return books

    def delete(self) -> None:
        self._db.delete()

    @classmethod
    def get_by_id(cls, id: Union[str, UUID]) -> BookModel:
        try:
            return cls._load(next(BookItem.query(hash_key=str(id))))
        except StopIteration:
            raise ResourceNotFound

    @classmethod
    def get_by_author(cls, author: str) -> List[BookModel]:
        return [cls._load(book) for book in BookItem.author_index.query(author)]

    @classmethod
    def get_all(cls) -> List[BookModel]:
        return [cls._load(book) for book in BookItem.scan()]
