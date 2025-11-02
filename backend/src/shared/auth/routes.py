"""Authentication routes for admin login."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from .auth_simple import create_access_token, verify_password

auth_router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request model"""

    password: str


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


@auth_router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
    """
    Login with admin password.

    Returns a JWT token that can be used for authentication.
    """
    if not verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"authenticated": True})
    return {"access_token": access_token, "token_type": "bearer"}
