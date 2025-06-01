from pydantic import BaseModel

from datetime import datetime

class InventoryBaseScheme(BaseModel):
    book_id: int

class InventoryReaderByIDScheme(BaseModel):
    reader_id: int
    
class IssueBookScheme(
        InventoryBaseScheme, 
        InventoryReaderByIDScheme,
    ):
    ...

class ReturnBookScheme(
        InventoryBaseScheme,
        InventoryReaderByIDScheme,
    ):
    id: int
    date_of_return: datetime
