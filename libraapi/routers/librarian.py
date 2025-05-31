from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import HTTPException


from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy import select

from dependencies.db import async_get_db
from utils.hashed import Hashed
from database.schemas.librarian import RegisterLibrarianScheme
from database.schemas.librarian import LoginLibrarianScheme
from database.schemas.librarian import LibrarianByEmailScheme
from database.schemas.token import JWTScheme
from database.models.librarian import LibrarianModel

from utils.jwt_utils import decode_jwt, encode_jwt

from typing import Optional

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
        
        
@router.post("/librarian/login/", response_model=JWTScheme)
async def librarian_login(
        scheme: LoginLibrarianScheme,
        db: AsyncSession = Depends(async_get_db)
    ):
    stmt = select(LibrarianModel).where(LibrarianModel.email == scheme.email)
    is_librarian = await db.execute(statement=stmt)
    result = is_librarian.scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверные данные"
        )
    
    hpwd = await Hashed().verify_password(
        password=scheme.password,
        hashed_password=result.password,
    )
    
    if not hpwd:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid user"
            )
    
    access_token = encode_jwt(
        payload={
            "sub": scheme.email,
            "type": "access"
        }
    )
    
    return JWTScheme(
        access_token=access_token,
        token_type="Bearer",
    )