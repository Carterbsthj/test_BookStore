from datetime import date
from sqlalchemy import Column, Integer, String, Date
from db.main import Base
from pydantic import BaseModel
from db.crud import AsyncCRUD


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_date = Column(Date)


class AuthorSchema(BaseModel):
    name: str
    birth_date: date


class AuthorCRUD(AsyncCRUD):
    def __init__(self, session):
        super().__init__(Author, session)
