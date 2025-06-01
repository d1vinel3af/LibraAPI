import uvicorn
import asyncio 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.book import router as book_router
from routers.reader import router as reader_router
from routers.librarian import router as librarian_router
from routers.inventory import router as inventory_router

from database.db import engine
from database.db import Base

app = FastAPI()

"""Подключаем роутеры"""
app.include_router(book_router, tags=["Книги"])
app.include_router(reader_router, tags=["Читатели"])
app.include_router(librarian_router, tags=["Библиотекари"])
app.include_router(inventory_router, tags=["Инвентаризация"])


"""Настройка корс"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def create_tables() -> None:
    """Создание всех необходимых таблицы"""
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(create_tables())
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True    
    )