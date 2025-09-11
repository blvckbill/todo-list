import bcrypt
from jose import jwt

from pydantic import EmailStr, field_validator

from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, Integer, LargeBinary, Text, Boolean
from sqlalchemy.orm import relationship
from todolist.models import TimeStampMixin, ToDoListBase, NameStr
from todolist.database.core import Base
from todolist.config import (
    TODOLIST_JWT_ALG,
    TODOLIST_JWT_EXP,
    TODOLIST_JWT_SECRET
)


def hash_password(password: str):
    """Hash a password using bcrypt"""
    pw = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)

class ToDoListUser(Base, TimeStampMixin):
    """SQLAlchemy model for a Todolist User."""

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(LargeBinary, nullable=False)

    def set_password(self, password: str):
        """Set a user password before saving to the db"""
        if not password:
            raise ValueError("Password must be provided")
        self.password = hash_password(password)

    def verify_password(self, password: str) -> bool:
        """Check if provided password matches hashed password"""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)
    
    @property
    def token(self):
        """Generate a JWT Token for the user"""
        now = datetime.now(timezone.utc)
        exp = (now + timedelta(seconds=TODOLIST_JWT_EXP)).timestamp()
        data = {
            "sub": str(self.id),
            "exp": exp,
            "email": self.email
        }
        return jwt.encode(data, TODOLIST_JWT_SECRET, algorithm=TODOLIST_JWT_ALG)
    
class TodoListUserTask(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and tasks"""

    id = Column(Integer, primary_key=True)
    todolist_user = relationship(ToDoListUser, backref="tasks")
    task_title = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)


class UserCreate(ToDoListBase):
    email: EmailStr
    password: str | None = None
    first_name: NameStr
    last_name: NameStr

    @field_validator("password", mode="before")
    @classmethod
    def hash(cls, v):
        """hash password before storing"""
        return hash_password(str(v))

class UserTasks(ToDoListBase):
    task_title: NameStr
    task_description: NameStr
    is_completed: bool

class UserInfo(ToDoListBase):
    """Response model for user info"""
    
    id: int
    email: EmailStr
    first_name: NameStr
    last_name: NameStr