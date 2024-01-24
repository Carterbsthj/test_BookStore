from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.author import AuthorCRUD, AuthorSchema
from db.main import async_session

router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session


@router.post("/", response_model=AuthorSchema, status_code=status.HTTP_201_CREATED)
async def create_author(author_data: AuthorSchema, session: AsyncSession = Depends(get_session)):
    author_crud = AuthorCRUD(session)
    author = await author_crud.create(**author_data.model_dump())
    return author


@router.get("/{author_id}", response_model=AuthorSchema)
async def read_author(author_id: int, session: AsyncSession = Depends(get_session)):
    author_crud = AuthorCRUD(session)
    author = await author_crud.read(author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@router.put("/{author_id}", response_model=AuthorSchema)
async def update_author(author_id: int, author_data: AuthorSchema, session: AsyncSession = Depends(get_session)):
    author_crud = AuthorCRUD(session)
    updated_author = await author_crud.update(author_id, **author_data.model_dump())
    if updated_author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return updated_author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session)):
    author_crud = AuthorCRUD(session)
    await author_crud.delete(author_id)
    return {"detail": "Author deleted successfully"}
