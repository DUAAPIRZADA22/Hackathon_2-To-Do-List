"""
Authentication service for business logic
"""

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from src.repositories.user import UserRepository
from src.auth.jwt import create_access_token


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        # bcrypt has a max password length of 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def signup(db: Session, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Token response with access token and user info

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if user already exists
        existing_user = UserRepository.get_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        existing_user = UserRepository.get_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Hash password and create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        new_user = UserRepository.create(db, user_data, hashed_password)

        # Refresh to get all fields including defaults
        db.refresh(new_user)

        # Create access token
        access_token = create_access_token(data={"sub": str(new_user.id)})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(new_user)
        )

    @staticmethod
    def signin(db: Session, user_data: UserLogin) -> TokenResponse:
        """
        Authenticate a user

        Args:
            db: Database session
            user_data: User login data

        Returns:
            Token response with access token and user info

        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = UserRepository.get_by_email(db, user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not AuthService.verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def get_current_user(user: User) -> UserResponse:
        """Get current authenticated user"""
        return UserResponse.model_validate(user)
