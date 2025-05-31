from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime

from datetime import datetime
from database.db import Base


class InventoryDataModel(Base):
    __tablename__ = "inventorydata"
    
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reader_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_issue: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    date_of_return: Mapped[datetime] = mapped_column(DateTime, nullable=True)

