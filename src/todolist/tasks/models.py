
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, select, func
from sqlalchemy.orm import relationship

from todolist.database.core import Base
from todolist.models import TimeStampMixin, NameStr
from todolist.auth.models import TodolistUser, ToDoListBase

from todolist.database.core import DbSession

from .service import (
    get_task_count
)

class Todolist(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and tasks"""

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("todolist_user.id"), nullable=False)
    title = Column(String, nullable=False)

    user = relationship("TodolistUser", back_populates="todolist")
    task = relationship("TodolistTasks", back_populates="todolist", cascade="all, delete-orphan")



class TodolistTask(Base, TimeStampMixin):
    """SQLAlchemy model that links tasks to a list"""

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("todolist.id"), nullable=False)
    task_title = Column(String, nullable=False)
    task_details = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)

    todolist = relationship("Todolist", back_populates="task")

class TodolistCreate(ToDoListBase):
    """Pydaantic model for user todolist"""

    id: int
    title: str

class TodotaskCreate(ToDoListBase):
    """Pydantic model for tasks"""
    id: int
    task_title: str
    task_details: str | None = None