from pydantic import BaseModel
from typing import Optional

class BookBaseSchemas(BaseModel):
    id: int
    

class AddBookSchemas(BaseModel):
    name: str
    author: str
    year_publication: Optional[int] = None
    isnb: Optional[str] = None
    amount: Optional[int] = None

    
class GetBookSchemas(BookBaseSchemas, AddBookSchemas):
    
    model_config = {
        'from_attributes': True
    }

class UpdateBookSchemas(BaseModel):
    amount: int
    