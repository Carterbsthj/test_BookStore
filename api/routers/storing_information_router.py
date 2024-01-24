from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.storing import StoringInformationCRUD, StoringInformationSchema, HistoryResponseSchema, \
    StoringHistoryCRUD, StoringHistory
from db.main import async_session
from api.services import *


router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session


@router.post("/", response_model=StoringInformationSchema, status_code=status.HTTP_201_CREATED)
async def create_storing_information(storing_data: StoringInformationSchema,
                                     session: AsyncSession = Depends(get_session)):
    storing_crud = StoringInformationCRUD(session)
    storing_info = await storing_crud.create(**storing_data.model_dump())
    return storing_info


@router.get("/{storing_id}", response_model=StoringInformationSchema)
async def read_storing_information(storing_id: int, session: AsyncSession = Depends(get_session)):
    storing_crud = StoringInformationCRUD(session)
    storing_info = await storing_crud.read(storing_id)
    if storing_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storing information not found")
    return storing_info


@router.put("/{storing_id}", response_model=StoringInformationSchema)
async def update_storing_information(storing_id: int, storing_data: StoringInformationSchema,
                                     session: AsyncSession = Depends(get_session)):
    storing_crud = StoringInformationCRUD(session)
    updated_storing_info = await storing_crud.update(storing_id, **storing_data.model_dump())
    if updated_storing_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storing information not found")
    return updated_storing_info


@router.delete("/{storing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storing_information(storing_id: int, session: AsyncSession = Depends(get_session)):
    storing_crud = StoringInformationCRUD(session)
    await storing_crud.delete(storing_id)
    return {"detail": "Storing information deleted successfully"}


@router.post("/leftover/add", status_code=201)
async def add_leftover(data: StoringInformationSchema, session: AsyncSession = Depends(get_session)):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    success = await update_leftover(book_id=data.book_id,
                                    quantity=data.quantity,
                                    session=session,
                                    created_at='2023-07-25',
                                    status='add')
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Leftover added successfully"}


@router.post("/leftover/remove", status_code=201)
async def remove_leftover(data: StoringInformationSchema, session: AsyncSession = Depends(get_session)):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    success = await update_leftover(book_id=data.book_id,
                                    quantity=data.quantity,
                                    session=session,
                                    created_at='2023-08-28',
                                    status='remove')
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Leftover removed successfully"}


@router.post("/leftovers/bulk", status_code=200)
async def bulk_update_leftovers(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    if file.filename.endswith('.xlsx'):
        result = await process_excel_file(file, session)
    elif file.filename.endswith('.txt'):
        result = await process_text_file(file, session)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    if "error" in result:
        raise HTTPException(status_code=result["error"]["code"], detail=result["error"]["message"])

    return {"message": "Bulk update processed successfully"}


@router.get("/history/get", response_model=HistoryResponseSchema)
async def get_history(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    book_key: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    start_date = start or date.min
    end_date = end or date.max

    query = select(StoringHistory).options(selectinload(StoringHistory.book))
    if book_key:
        query = query.filter(StoringHistory.book_id == book_key)
    history_records = await session.execute(query)
    history_records = history_records.scalars().all()

    history_by_book = {}
    for record in history_records:
        record_date = record.created_at.date()
        if start_date <= record_date <= end_date:
            book_id = record.book_id
            if book_id not in history_by_book:
                history_by_book[book_id] = {
                    'book': {
                        'key': record.book.id,
                        'title': record.book.title,
                        'barcode': record.book.barcode
                    },
                    'history': []
                }
            history_by_book[book_id]['history'].append({
                'date': record_date,
                'quantity': record.updated_value,
                'status': record.status,
                'quantity_after_change': record.quantity_after_change
            })

    for book_id, data in history_by_book.items():
        data['history'].sort(key=lambda x: x['date'])
        data['start_balance'] = data['history'][0]['quantity_after_change'] if data['history'] else 0
        data['end_balance'] = data['history'][-1]['quantity_after_change'] if data['history'] else 0
        data['history'].sort(key=lambda x: x['date'], reverse=True)

    return {'history': [data for data in history_by_book.values()]}


