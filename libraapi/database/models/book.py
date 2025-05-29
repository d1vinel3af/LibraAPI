from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Identity

from database.db import Base



class BookModels(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    year_publication: Mapped[int] = mapped_column(Integer, nullable=True)
    isnb: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    