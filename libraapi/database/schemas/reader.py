from pydantic import BaseModel

from pydantic import EmailStr


class GetByIDReaderScheme(BaseModel):
    id: int

class GetByEmailReaderScheme(BaseModel):
    email: EmailStr
    
class AddReaderScheme(GetByEmailReaderScheme):
    fullname: str
    
class GetReaderScheme(
        GetByIDReaderScheme,
        AddReaderScheme
    ):
    model_config = {
        'from_attributes': True
    }