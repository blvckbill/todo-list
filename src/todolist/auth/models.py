from sqlalchemy import Column, String, Integer, LargeBinary, Text, Boolean
from sqlalchemy.orm import relationship
from todolist.models import TimeStampMixin
from todolist.database.core import Base

class ToDoListUser(Base, TimeStampMixin):
    """SQLAlchemy model for a Todolist User."""

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(LargeBinary, nullable=False)

class TodoListUserTask(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and tasks"""

    id = Column(Integer, primary_key=True)
    todolist_user = relationship(ToDoListUser, backref="tasks")
    task_title = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)

