
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from todolist.database.core import Base
from todolist.models import TimeStampMixin, NameStr
from todolist.auth.models import TodolistUser, ToDoListBase


class TodolistuserTask(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and tasks"""

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("todolist_user.id"), nullable=False)
    task_title = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)

    user = relationship(TodolistUser, back_populates="task")


class UserTasks(ToDoListBase):
    """Pydaantic model for user tasks"""

    task_title: NameStr
    task_description: NameStr
    is_completed: bool