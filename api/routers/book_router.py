from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.models.author import AuthorSchema, AuthorCRUD
from db.models.book import BookCRUD, BookSchema, BookSearchResponseSchema, BookResponse, BookSearchItemSchema
from db.main import async_session
from db.models.storing import StoringInformationCRUD


router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookSchema, session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    storing_crud = StoringInformationCRUD(session)

    book = await book_crud.create(**book_data.model_dump())

    await storing_crud.create(book_id=book.id, quantity=1)

    await storing_crud.add_history_record(book_id=book.id, updated_value=1)

    return book


@router.get("/book/{book_id}", response_model=BookSchema)
async def read_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    book = await book_crud.read(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: int, book_data: BookSchema, session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    updated_book = await book_crud.update(book_id, **book_data.model_dump())
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated_book


@router.get("/books/", response_model=List[BookResponse])
async def read_all_books(session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    books = await book_crud.read_all()
    return [BookResponse(key=book.id, title=book.title, barcode=book.barcode) for book in books]


@router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    await book_crud.delete(book_id)
    return {"detail": "Book deleted successfully"}


@router.get("/barcode", response_model=BookSearchResponseSchema)
async def search_book_by_barcode(barcode: str, session: AsyncSession = Depends(get_session)):
    book_crud = BookCRUD(session)
    storing_crud = StoringInformationCRUD(session)
    books = await book_crud.search_by_barcode(barcode)
    author_crud = AuthorCRUD(session)
    items = []
    for book in books:
        storing_info = await storing_crud.read(book.id)
        quantity = storing_info.quantity if storing_info else 0
        author = await author_crud.read(book.author_id)
        item = BookSearchItemSchema(
            key=book.id,
            barcode=book.barcode,
            title=book.title,
            publish_year=book.publish_year,
            author=AuthorSchema(name=author.name, birth_date=author.birth_date),
            quantity=quantity
        )
        items.append(item)

    return BookSearchResponseSchema(found=len(items), items=items)
