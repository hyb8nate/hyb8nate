"""Simple authentication using admin password from environment variable."""

import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.shared.settings import settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str) -> bool:
    """Verify if password matches admin password"""
    return plain_password == settings.ADMIN_PASSWORD


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("authenticated") is not True:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user (always admin)"""
    return {"authenticated": True, "role": "admin"}
