from sqlalchemy import Column, String
from todo.models import TimeStampMixin


class ToDoUser(Base, TimeStampMixin):
    