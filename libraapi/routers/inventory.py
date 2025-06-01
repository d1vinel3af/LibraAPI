from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import insert

from database.models.inventory import InventoryDataModel
from database.models.book import BookModels
from database.models.reader import ReaderModel
from database.schemas.inventory import IssueBookScheme
from database.schemas.inventory import ReturnBookScheme
from database.schemas.inventory import InventoryReaderByIDScheme

from dependencies.db import async_get_db
from utils.validate import get_current_user


router = APIRouter()



@router.post("/inventory/issue/")
async def issue_book(
        scheme: IssueBookScheme,
        db: AsyncSession = Depends(async_get_db),
        current_user: dict = Depends(get_current_user)
    ):
    
    #Проводим проверку книг перед выдачей
    stmt_amount_book = select(BookModels).where(BookModels.id == scheme.book_id)
    inject_book = await db.execute(statement=stmt_amount_book)
    result_book = inject_book.scalar_one_or_none()
    
    if result_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Книги с таким id не существует"
            }
        )
   
    #Проводим проверку на наличие читателя
    stmt_is_reader = select(ReaderModel).where(ReaderModel.id == scheme.reader_id)
    inject_reader = await db.execute(statement=stmt_is_reader)
    result_reader = inject_reader.scalar_one_or_none()
    
    if result_reader is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Такого читателя нет в системе"
            }
        )
    
    # Проверяем сколько у читателя уже взято книг и может ли он взять ещё
    stmt_amount_book_reader = select(InventoryDataModel)\
                        .where(
                            InventoryDataModel.reader_id == scheme.reader_id,
                            InventoryDataModel.date_of_return == None
                            )
    inject_amount_book_reader = await db.execute(statement=stmt_amount_book_reader)
    
    #Получаем кол-во не сданных книг
    result_amount_book_reader = len(inject_amount_book_reader.scalars().all())
    
    if result_amount_book_reader == 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Превышен лимит взятых книг"
            }
        )
    
    # Проверяем что книги есть в наличии
    if result_book.amount == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "На данный момент книг нет в наличии"
            }
        )
        
    # Записываем данные о выдачи книги
    stmt_inventory_add = insert(InventoryDataModel).values(scheme.model_dump())
    await db.execute(statement=stmt_inventory_add)
    await db.commit()
    
    # Обновляем кол-во книг из бд
    
    new_amount_book = int(result_book.amount) - 1
    
    stmt_update_amount_book = update(BookModels)\
                            .where(BookModels.id == scheme.book_id)\
                            .values(amount = new_amount_book)
    await db.execute(statement=stmt_update_amount_book)
    await db.commit()
    
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "issue": "Типа выдана книга"
        }
    )
    
@router.post("/inventory/return/")
async def return_book(
        scheme: ReturnBookScheme,
        db: AsyncSession = Depends(async_get_db),
        current_user: dict = Depends(get_current_user)
    ):
    
    try:
        # Записываем, что книгу вернули
        stmt_return_book = update(InventoryDataModel)\
                        .where(InventoryDataModel.id == scheme.id)\
                        .values(date_of_return = datetime.now())
        await db.execute(statement=stmt_return_book)
        await db.commit()
        
        
        # Возвращаем книгу на "полку"
        stmt_amount_book = select(BookModels).where(BookModels.id == scheme.book_id)
        inject_book = await db.execute(statement=stmt_amount_book)
        result_book = inject_book.scalar_one_or_none()
        
        
        new_amount_book = int(result_book.amount) + 1
        
        stmt_amount_book = update(BookModels)\
                        .where(BookModels.id == scheme.book_id)\
                        .values(amount = new_amount_book)
        await db.execute(statement=stmt_amount_book)
        await db.commit()

        
    
    
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Непредвиденная ошибка: {error}"
            }
        )
    
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "return": "Типа книга забрана"
        }
    )