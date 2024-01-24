from typing import Optional, List
from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from db.main import Base
from pydantic import BaseModel
from db.models.author import AuthorSchema
from db.crud import AsyncCRUD


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    publish_year = Column(Integer)
    author_id = Column(Integer, ForeignKey('authors.id'))
    barcode = Column(String)
    author = relationship("Author")


class BookSchema(BaseModel):
    title: str
    publish_year: int
    author_id: int
    barcode: str


class BookSearchItemSchema(BaseModel):
    key: int
    barcode: Optional[str]
    title: str
    publish_year: int
    author: AuthorSchema
    quantity: int


class BookSearchResponseSchema(BaseModel):
    found: int
    items: List[BookSearchItemSchema]


class BookCRUD(AsyncCRUD):
    def __init__(self, session):
        super().__init__(Book, session)

    async def search_by_barcode(self, barcode: str) -> List[Book]:
        query = select(Book).where(Book.barcode.like(f"{barcode}%")).order_by(Book.barcode)
        result = await self.session.execute(query)
        books = result.scalars().all()
        return books

    async def read_all(self) -> List[Book]:
        query = select(Book)
        result = await self.session.execute(query)
        return result.scalars().all()


class BookResponse(BaseModel):
    key: int
    title: str
    barcode: str
