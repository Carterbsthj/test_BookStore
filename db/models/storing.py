from datetime import date, datetime
from typing import List
from sqlalchemy import Column, Integer, ForeignKey, func, DateTime, select, String
from sqlalchemy.orm import relationship
from db.main import Base
from pydantic import BaseModel
from db.models.book import BookResponse
from db.crud import AsyncCRUD


class StoringInformation(Base):
    __tablename__ = 'storing_information'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    quantity = Column(Integer)
    book = relationship("Book")


class StoringInformationSchema(BaseModel):
    book_id: int
    quantity: int


class StoringInformationCRUD(AsyncCRUD):
    def __init__(self, session):
        super().__init__(StoringInformation, session)

    async def add_history_record(self, book_id: int, updated_value: int):
        history_record = StoringHistory(
            book_id=book_id,
            quantity_after_change=updated_value,
            updated_value=updated_value,
            created_at=datetime.now()
        )
        self.session.add(history_record)
        await self.session.commit()


class StoringHistory(Base):
    __tablename__ = 'storing_history'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    quantity_after_change = Column(Integer)
    updated_value = Column(Integer)
    status = Column(String, default='Pending')
    created_at = Column(DateTime, default=func.now())
    book = relationship("Book")


class StoringHistoryCRUD(AsyncCRUD):
    def __init__(self, session):
        super().__init__(StoringHistory, session)

    async def get_history_for_book(self, book_id: int):
        try:
            query = select(StoringHistory).filter(StoringHistory.book_id == book_id).order_by(
                StoringHistory.date.desc())

            result = await self.session.execute(query)
            storing_history_entries = result.scalars().all()

            return storing_history_entries
        except Exception as e:
            raise e

    async def add_history_record(self, book_id: int, updated_value: int, quantity_after_change: int, created_at: date):
        history_record = StoringHistory(
            book_id=book_id,
            quantity_after_change=quantity_after_change,
            updated_value=updated_value,
            created_at=created_at,
        )
        self.session.add(history_record)
        await self.session.commit()


class HistoryRecordSchema(BaseModel):
    book_id: int
    quantity_after_change: int
    updated_value: int
    created_at: date
    status: str


class HistoryEntry(BaseModel):
    date: date
    quantity: int
    status: str


class HistoryRecord(BaseModel):
    book: BookResponse
    start_balance: int
    end_balance: int
    history: List[HistoryEntry]


class HistoryResponseSchema(BaseModel):
    history: List[HistoryRecord]
