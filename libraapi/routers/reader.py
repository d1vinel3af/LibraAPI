from fastapi import APIRouter
from fastapi import status
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy import insert

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dependencies.db import async_get_db

from database.schemas.reader import AddReaderSchema
from database.models.reader import ReaderModel



router = APIRouter()


@router.post("/reader/")
async def add_reader(
        scheme: AddReaderSchema, 
        db: AsyncSession = Depends(async_get_db)
    ):
    """
    Добавляет нового читателя в систему.

    Параметры:
    - reader_data: Данные читателя согласно схеме AddReaderSchema, включая:
        - full_name: Полное имя читателя (обязательно)
        - email: Email читателя (обязательно)

    Возвращает:
        - JSON-объект с сообщением об успешном добавлении
        - Код статуса 201 Created при успешном добавлении

    Ошибки:
        HTTPException: 500 - Внутренняя ошибка сервера при возникновении непредвиденных ситуаций
        HTTPException: 409 - Конфликт, если читатель с такими email уже существует
    
    Пример тела запроса:
    json:
    {
        "full_name": "Иванов Иван Иванович",
        "email": "ivanov@example.com",
    }
    """
    try:
        stmt = insert(ReaderModel).values(scheme.model_dump())
        await db.execute(statement=stmt)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "reader": "Пользователь добавлен"
            }
        )
    except IntegrityError:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Такой пользователь уже существует"
            )
    
    except Exception as error:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Неизвестная ошибка: {error}"
            )