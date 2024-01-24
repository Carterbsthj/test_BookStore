from faker import Faker
import asyncio
from db.main import async_session
from db.models.author import AuthorCRUD, AuthorSchema
from db.models.book import BookCRUD, BookSchema
from db.models.storing import StoringInformationCRUD, StoringInformationSchema, StoringHistoryCRUD, HistoryRecordSchema

fake = Faker()


async def create_authors(session, n=20):
    author_crud = AuthorCRUD(session)
    for _ in range(n):
        author_data = AuthorSchema(
            name=fake.name(),
            birth_date=fake.date_of_birth(minimum_age=100, maximum_age=300).isoformat()
        )
        await author_crud.create(**author_data.model_dump())


async def create_books_storing_info_and_history(session, n=100):
    book_crud = BookCRUD(session)
    storing_crud = StoringInformationCRUD(session)
    storing_history_crud = StoringHistoryCRUD(session)

    for _ in range(n):
        # Create a book
        book_data = BookSchema(
            title=fake.sentence(nb_words=4),
            publish_year=fake.year(),
            author_id=fake.random_int(min=1, max=20),
            barcode=fake.bothify(text='######')
        )
        book = await book_crud.create(**book_data.model_dump())
        quantity = fake.random_int(min=1, max=100)

        storing_info_data = StoringInformationSchema(
            book_id=book.id,  # Use the book schema
            quantity=quantity
        )
        await storing_crud.create(**storing_info_data.model_dump())

        storing_history_data = HistoryRecordSchema(
            book_id=book.id,
            quantity_after_change=quantity,
            updated_value=quantity,
            created_at=fake.date_between(start_date='-1y', end_date='now'),
            status='add'
        )
        await storing_history_crud.create(**storing_history_data.model_dump())


async def main():
    async with async_session() as session:
        await create_authors(session)
        await create_books_storing_info_and_history(session)


if __name__ == "__main__":
    asyncio.run(main())
