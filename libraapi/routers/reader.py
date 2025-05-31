from fastapi import APIRouter
from fastapi import status
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import delete

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dependencies.db import async_get_db

from database.schemas.reader import AddReaderScheme
from database.schemas.reader import GetByEmailReaderScheme
from database.schemas.reader import GetReaderScheme
from database.models.reader import ReaderModel

from utils.validate import get_current_user

router = APIRouter()


@router.post("/reader/")
async def add_reader(
        scheme: AddReaderScheme, 
        db: AsyncSession = Depends(async_get_db),
        current_user: dict = Depends(get_current_user)
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

@router.post("/reader/data")
async def get_reader_by_email(
        scheme: GetByEmailReaderScheme,
        db: AsyncSession = Depends(async_get_db),
        current_user: dict = Depends(get_current_user)
    ):
    """
    Получает информацию о читателе по его email.

    Параметры:
    - scheme: Данные для поиска читателя согласно схеме GetByEmailReaderScheme, включая:
        - email: Email читателя (обязательно)

    Возвращает:
        - JSON-объект с данными найденного читателя, включая:
            - id: Идентификатор читателя
            - full_name: Полное имя читателя
            - email: Email читателя
        - Код статуса 200 OK при успешном поиске

    Ошибки:
        HTTPException: 404 - Если читатель с указанным email не найден
        HTTPException: 500 - Внутренняя ошибка сервера при возникновении непредвиденных ситуаций

    Пример тела запроса:
    json:
    {
        "email": "ivanov@example.com"
    }

    Пример успешного ответа:
    json:
    {
        "reader": {
            "id": 1,
            "full_name": "Иванов Иван Иванович",
            "email": "ivanov@example.com",
            ...
        }
    }
    """
    try:
        stmt = select(ReaderModel).where(ReaderModel.email == scheme.email).execution_options(expire_on_commit=False)
        result = await db.execute(statement=stmt)
        reader = result.scalar_one_or_none()
        if reader is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Читатель не найден"
            )
        result = GetReaderScheme.model_validate(reader).model_dump()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "reader": result
            }
        )
    except Exception as error:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Неизвестная ошибка: {error}"
            )
        
@router.delete("/reader/{reader_id}")
async def delete_reader_by_id(
        reader_id: int,
        db: AsyncSession = Depends(async_get_db),
        current_user: dict = Depends(get_current_user)
    ):
    
    """
    Удаляет читателя из бд.

    Параметры:
        reader_id: int

    Возвращает:
        json:
        - delete: successfully <- успешное удаление

    Ошибки:
        HTTPException: 404 ошибка если читатель с таким id не найдена
        HTTPException: 500 ошибка при возникновении непредвиденных ситуаций
    """
    
    stmt = delete(ReaderModel).where(ReaderModel.id == reader_id).returning(ReaderModel)
    result_delete_reader = await db.execute(statement=stmt)
    if result_delete_reader.scalar_one_or_none() is None:
        raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Такого пользователя не существует"
                )
    await db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
                "delete": "successfully"
            }
    )