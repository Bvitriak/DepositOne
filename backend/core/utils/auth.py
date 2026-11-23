import jwt
from fastapi import Header, HTTPException

import config


def decode_access_token(token):
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])


def require_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="authorization required")
    token = authorization[len("Bearer "):]
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    return {"id": payload["user_id"], "username": payload["username"]}
