"""
Task model for database
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class Task(Base):
    """Task model"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo")  # todo, in_progress, done
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to User
    user = relationship("User", backref="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
