"""
Authentication API routes
"""

import logging
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.models.schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    AuthResponse
)
from src.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - **email**: User's email address (must be unique)
    - **username**: Desired username (must be unique, 3-50 characters)
    - **password**: Password (min 6 characters)
    """
    return AuthService.signup(db, user_data)


@router.post("/auth/signin", response_model=TokenResponse)
def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Sign in with email and password

    - **username**: Email address
    - **password**: Password
    """
    import traceback
    try:
        logger.info(f"Signin attempt for: {form_data.username}")
        user_data = UserLogin(email=form_data.username, password=form_data.password)
        result = AuthService.signin(db, user_data)
        logger.info(f"Signin successful for user ID: {result.user.id}")
        return result
    except Exception as e:
        logger.error(f"Signin error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        raise


@router.post("/auth/signout", response_model=AuthResponse)
def signout():
    """
    Sign out the current user

    Client should discard the token
    """
    return AuthResponse(message="Successfully signed out")


@router.get("/auth/me", response_model=UserResponse)
def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current authenticated user's information

    Requires valid JWT token
    """
    return AuthService.get_current_user(current_user)
