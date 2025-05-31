import jwt
from core.security import auth_jwt

from datetime import timedelta
from datetime import datetime
from datetime import timezone

def encode_jwt(
            payload:dict, 
            private_key: str = auth_jwt.private_key.read_text(), 
            algorithm: str = auth_jwt.algorithm,
            expire_timedelta: timedelta | None = None, 
            expire_minutes: int = auth_jwt.access_token_exmpire_min,
        ):
    to_encode = payload.copy()
    
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    
    to_encode.update(
        exp = expire,
        iat = now,
    )
    
    encoded = jwt.encode(
        payload=to_encode, 
        key=private_key, 
        algorithm=algorithm
    )
    
    return encoded
    
    
def decode_jwt(
            token:str | bytes, 
            public_key: str = auth_jwt.public_key.read_text(), 
            algorithm: str = auth_jwt.algorithm
        ):
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm]
    )
    
    return decoded




