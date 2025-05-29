from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import DATABASE


Base = declarative_base()

dbprod = DATABASE['dbprod']

engine = create_async_engine(
        url=f"{dbprod['stack']}://{dbprod['dbuser']}:{dbprod['dbpassword']}@{dbprod['dbhost']}:{dbprod['dbport']}/{dbprod['dbname']}",
        echo=True
    )

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)