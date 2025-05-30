from pydantic import BaseModel
from pydantic import EmailStr

class LibrarianByIDScheme(BaseModel):
    id: int
    
    
class LibrarianByEmailScheme(BaseModel):
    email: EmailStr
    
class RegisterLibrarianScheme(LibrarianByEmailScheme):
    password: str 
    
class LoginLibrarianScheme(RegisterLibrarianScheme):
    ...
