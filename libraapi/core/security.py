from pathlib import Path
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer


from .config import BASE_DIR

class AuthJWT(BaseModel):
    private_key: Path = BASE_DIR / "core" / "certs" / "private.pem"
    public_key: Path = BASE_DIR / "core" / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_exmpire_min: int = 15


auth_jwt = AuthJWT()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="librarian/login/")


