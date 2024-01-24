from datetime import date, datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models.storing import StoringInformation, HistoryRecordSchema, StoringHistoryCRUD
from db.models.book import Book
import pandas as pd


async def update_leftover(session: AsyncSession, book_id=0, quantity: int = 0,
                          created_at: date = '2024-01-01', status: str = 'add', barcode: str = 'adc') -> bool:

    if barcode != 'abc':
        book_query = select(Book).where(Book.barcode == barcode)
    else:
        book_query = select(Book).where(Book.id == book_id)
    if quantity < 0:
        status = 'remove'
    book_result = await session.execute(book_query)
    book = book_result.scalars().first()
    storing_history_crud = StoringHistoryCRUD(session)
    if not book:
        return False

    storing_info_query = select(StoringInformation).where(StoringInformation.book_id == book.id)
    storing_info_result = await session.execute(storing_info_query)
    storing_info = storing_info_result.scalars().first()

    if storing_info:
        if status == 'add':
            storing_info.quantity += quantity
        elif status == 'remove':
            storing_info.quantity -= quantity
        else:
            storing_info.quantity = quantity
        quantity_after_change = storing_info.quantity
    else:
        storing_info = StoringInformation(book_id=book.id, quantity=quantity)
        quantity_after_change = quantity
        session.add(storing_info)

    storing_history_entry = HistoryRecordSchema(book_id=book.id,
                                                quantity_after_change=quantity_after_change,
                                                updated_value=quantity,
                                                created_at=created_at,
                                                status=status)

    await storing_history_crud.create(**storing_history_entry.model_dump())

    await session.commit()
    return True


def parse_txt_line(line, expected_prefix):
    if not line.startswith(expected_prefix):
        return None
    return line[len(expected_prefix):].strip()


async def process_text_file(file: UploadFile, session: AsyncSession):
    content = await file.read()
    lines = content.decode('utf-8').splitlines()

    updates = {}
    current_barcode = None

    for line in lines:

        if line.startswith("BRC"):
            current_barcode = line[3:].strip()
        elif line.startswith("QNT") and current_barcode:
            try:
                quantity = int(line[3:].strip())
                updates[current_barcode] = updates.get(current_barcode, 0) + quantity
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid quantity for barcode {current_barcode}")

    for barcode, quantity in updates.items():
        if not await update_leftover(session, quantity=quantity, created_at=date.today(), barcode=barcode):
            raise HTTPException(status_code=404, detail=f"Barcode {barcode} not found in the database")

    return {"message": "File processed successfully"}


async def process_excel_file(file: UploadFile, session: AsyncSession):
    df = pd.read_excel(file.file)
    if 'barcode' not in df.columns or 'quantity' not in df.columns:
        raise HTTPException(status_code=400, detail="Excel file must contain 'barcode' and 'quantity' columns.")

    for index, row in df.iterrows():
        barcode = row['barcode']
        quantity = row['quantity']

        if pd.isna(barcode):
            continue

        if not pd.isna(quantity) and not isinstance(quantity, (int, float)):
            raise HTTPException(status_code=400, detail=f"Row {index + 1}: Quantity is not a number.")

        if not await update_leftover(session, barcode=barcode, quantity=int(quantity)):
            raise HTTPException(status_code=404,
                                detail=f"Row {index + 1}: Barcode {barcode} not found in the database.")

    return {"message": "Excel file processed successfully"}


async def calculate_balance(history_records, start_date: date, end_date: date):
    start_balance = end_balance = 0
    for record in history_records:
        record_date = record['date']
        if isinstance(record_date, datetime):
            record_date = record_date.date()

        if record_date < start_date:
            start_balance += record['quantity']
        if record_date <= end_date:
            end_balance += record['quantity']
    return start_balance, end_balance
