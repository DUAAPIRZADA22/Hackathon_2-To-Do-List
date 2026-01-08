"""
User repository for data access operations
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import User
from src.models.schemas import UserCreate


class UserRepository:
    """Repository for User model"""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create(db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
