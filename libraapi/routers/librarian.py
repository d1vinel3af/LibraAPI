from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import HTTPException


from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy import select

from dependencies.db import async_get_db
from utils.hashed import Hashed
from database.schemas.librarian import RegisterLibrarianScheme
from database.models.librarian import LibrarianModel


router = APIRouter()


@router.post("/librarian/register/")
async def librarian_register(
        scheme: RegisterLibrarianScheme,
        db: AsyncSession = Depends(async_get_db)
    ):

    try:
        # Проверяем, существует ли пользователь с таким email
        stmt_get_by_email = select(LibrarianModel).where(LibrarianModel.email == scheme.email)
        result = await db.execute(statement=stmt_get_by_email)
        is_librarian = result.scalar_one_or_none()
        
        if is_librarian is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
        
        
        # "Регистрация" библиотекоря
        userdata = {
            "email": scheme.email,
            "password": await Hashed().hashed_password(scheme.password)
        }
        
        stmt_add_librarian = insert(LibrarianModel).values(**userdata)
        await db.execute(statement=stmt_add_librarian)
        await db.commit()
        
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "librarian": "Библиотекарь успешно зарегестрирован"
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"непредвиденная ошибка: {error}"
            }
        )
        
        
@router.post("/librarian/login/")
async def librarian_login():
    ...