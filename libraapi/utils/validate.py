from fastapi import Depends
from typing import Optional
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from utils.jwt_utils import decode_jwt


async def get_current_user(token: str = Depends(HTTPBearer())) -> Optional[dict]:
    try:
        payload = decode_jwt(token.credentials)
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=403, 
                detail="Cannot use refresh token as access token"
            )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token"
        )

