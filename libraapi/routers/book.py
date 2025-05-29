from fastapi import APIRouter
from fastapi import status
from fastapi import Depends
from fastapi import Path
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.schemas.book import AddBookSchemas
from database.schemas.book import GetBookSchemas
from database.schemas.book import UpdateBookSchemas

from database.models.book import BookModels

from dependencies.db import async_get_db

router = APIRouter()


@router.post("/book/")
async def add_book(schema: AddBookSchemas, db: AsyncSession = Depends(async_get_db)):
    """
    Добавляет новую книгу в каталог.

    Параметры:
    - book_data: Данные книги согласно схеме AddBookSchema, включая:
        - name: Название книги (обязательно)
        - author: Автор книги (обязательно)
        - year_publication: Год публикации (опционально)
        - isnb: ISBN книги (опционально)
        - amount: Количество экземпляров (по умолчанию 0)

    Возвращает:
        - Сообщение об успешном добавлении
        - Код статуса 201 Created при успешном добавлении

    Ошибки:
        HTTPException: 500 ошибка при возникновении непредвиденных ситуаций 
        HTTPException: 409 если запись с уникальными параметрами в бд уже существует
    
    Пример тела запроса:
    json:
    {
        "name": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "year_publication": 1866,
        "isnb": "978-5-699-12345-6",
        "amount": 3
    }
    
    """
    try:
        stmt = insert(BookModels).values(schema.model_dump())
        await db.execute(statement=stmt)
        await db.commit()

        if schema.amount < 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Кол-во книг не может быть меньше нуля"
            )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "details": "success created"
            }
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Книга с ISBN {schema.isnb} уже существует"
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {error}"
        )

@router.get("/book/")
async def get_books(db: AsyncSession = Depends(async_get_db)):
    """
    Получает список всех книг из базы данных.

    Параметры:
        -

    Возвращает:
        Ответ в формате JSON, содержащий список книг:
        - books (list): Список всех книг с полной информацией о каждой:
            - id (int): Уникальный идентификатор книги
            - name (str): Название книги
            - author (str): Автор книги
            - year_publication (int, optional): Год публикации
            - isnb (str, optional): Международный стандартный номер книги
            - amount (int): Количество доступных экземпляров

    Ошибки:
        HTTPException: 500 ошибка при возникновении непредвиденных ситуаций
    """
    try:
        stmt = select(BookModels)
        books = await db.execute(statement=stmt)
        rows = books.scalars().all()
        books_list = [
            GetBookSchemas.model_validate(row).model_dump() for row in rows
        ]
            
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "books": books_list
            }
        )
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {error}"
        )
        
        
@router.get("/book/{book_id}")
async def get_book_by_id(
        book_id: int = Path(..., gt=0),
        db: AsyncSession = Depends(async_get_db)
    ):
    """
    Получает информацию о книге из бд по id.

    Параметры:
        book_id: int, больше 0

    Возвращает:
        Ответ в формате JSON, содержащий список книг:
        - book (dict):
            - id (int): Уникальный идентификатор книги
            - name (str): Название книги
            - author (str): Автор книги
            - year_publication (int, optional): Год публикации
            - isnb (str, optional): Международный стандартный номер книги
            - amount (int): Количество доступных экземпляров

    Ошибки:
        HTTPException: 404 ошибка если книга с таким id не найдена
        HTTPException: 500 ошибка при возникновении непредвиденных ситуаций
    """
    
    try:
        stmt = select(BookModels).where(BookModels.id == book_id).execution_options(expire_on_commit=False)
        result = await db.execute(statement=stmt)
        book = result.scalar_one_or_none()
        
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Книга не найдена"
            )
            
        result = GetBookSchemas.model_validate(book).model_dump()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "book": result
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {error}"
        )
        
@router.delete("/book/{book_id}")
async def delete_book(
        book_id: int = Path(..., gt=0),
        db: AsyncSession = Depends(async_get_db)
    ):
    """
    Удаляет книгу из бд.

    Параметры:
        book_id: int, больше 0

    Возвращает:
        json:
        - delete: successfully <- успешное удаление

    Ошибки:
        HTTPException: 404 ошибка если книга с таким id не найдена
        HTTPException: 500 ошибка при возникновении непредвиденных ситуаций
    """
    
    try:
        stmt = delete(BookModels).where(BookModels.id == book_id).returning(BookModels)
        result_delete_book = await db.execute(statement=stmt)
        
        
        if result_delete_book.scalar_one_or_none() is None:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Книга не найдена"
                )
            
        await db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "delete": "successfully"
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {error}"
        )
        
    
@router.patch("/book/{book_id}")
async def update_book(
        schema: UpdateBookSchemas,
        book_id: int = Path(..., gt=0),
        db: AsyncSession = Depends(async_get_db)
    ):
    
    """
    Обновляет данные книги в базе данных.

    Параметры:
        schema: UpdateBookSchemas - схема с данными для обновления книги
        book_id: int - ID книги (должен быть больше 0)

    Возвращает:
        JSONResponse:
        - update: "successfully" - при успешном обновлении

    Ошибки:
        HTTPException: 
        - 404 (Not Found) - если книга с указанным ID не найдена
        - 409 (Conflict) - если количество книг указано меньше нуля
        - 500 (Internal Server Error) - при возникновении непредвиденных ошибок
    """
    
    
    try:
        stmt_get_book = select(BookModels).where(BookModels.id == book_id).execution_options(expire_on_commit=False)
        result = await db.execute(statement=stmt_get_book)
        book = result.scalar_one_or_none()
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Книга не найдена"
            )
        
        if schema.amount < 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Кол-во книг не может быть меньше нуля"
            )
        
        stmt = update(BookModels).where(BookModels.id == book_id).values(schema.model_dump())
        await db.execute(statement=stmt)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "delete": "successfully"
            }
        )
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {error}"
        )