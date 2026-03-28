"""
Authentication API routes (Using sync database for Phase I/II User model)
"""

import logging
import bcrypt
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.config import settings
from src.core.database import get_db
from src.models.user import User as PhaseIUser
from src.models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse

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
    # Check if email exists
    existing_user = db.query(PhaseIUser).filter(PhaseIUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    existing_user = db.query(PhaseIUser).filter(PhaseIUser.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Hash password
    password_bytes = user_data.password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Create user
    new_user = PhaseIUser(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed.decode('utf-8'),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    from jose import jwt
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode = {"sub": str(new_user.id), "exp": expire}
    access_token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


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
    from jose import jwt, JWTError

    # Get user by email
    user = db.query(PhaseIUser).filter(PhaseIUser.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    try:
        if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode = {"sub": str(user.id), "exp": expire}
    access_token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/auth/signout")
def signout():
    """
    Sign out the current user

    Client should discard the token
    """
    return {"message": "Successfully signed out"}


@router.get("/auth/test")
def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "error": str(e)}
