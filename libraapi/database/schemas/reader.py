from pydantic import BaseModel

from pydantic import EmailStr


class GetByIDReader(BaseModel):
    id: int

class GetByEmailReaderSchema(BaseModel):
    email: EmailStr
    
class GetByFullnameReaderSchema(BaseModel):
    fullname: str

class AddReaderSchema( 
        GetByEmailReaderSchema, 
        GetByFullnameReaderSchema
    ):
    pass
    
    
