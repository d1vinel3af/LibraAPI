from pydantic import BaseModel

class JWTScheme(BaseModel):
    access_token: str
    token_type: str