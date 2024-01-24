from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio

Base = declarative_base()
engine = create_async_engine('sqlite+aiosqlite:///./db.db', echo=True)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

