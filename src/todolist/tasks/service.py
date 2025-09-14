

from .models import TodolistuserTask

def get(*, db_session, task_id: int) -> TodolistuserTask:
    """Returns a task based on the given task id"""
    return db_session.query(TodolistuserTask).filter(TodolistuserTask.id == task_id).one_or_none()

def create(*, db_session):
    pass