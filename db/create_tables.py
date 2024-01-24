import asyncio
from db.main import engine, Base
from db.models.book import Book  # don't remove this import
from db.models.author import Author  # don't remove this import
from db.models.storing import StoringInformation  # don't remove this import
from db.models.storing import StoringHistory  # don't remove this import


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
