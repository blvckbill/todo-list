
from sqlalchemy import select, func

from todolist.database.core import DbSession

from .models import Todolist, TodolistTask, TodolistCreate, TodotaskCreate

def get(*, db_session, list_id: int) -> Todolist:
    """Returns a Todo list"""
    return db_session.query(Todolist).filter(Todolist.id == list_id)

def get_tasks(*, db_session, list_id: int) -> TodolistTask:
    """Returns the tasks linked to a TodoList"""
    return db_session.query(TodolistTask).filter(TodolistTask.list_id == list_id).all()

def get_completed(*, db_session) -> TodolistTask:
    """Return completed Tasks"""
    return db_session.query(TodolistTask).filter(TodolistTask.is_completed == True).all()

def get_starred(*, db_session) -> TodolistTask:
    """Return starred tasks"""
    return db_session.query(TodolistTask).filter(TodolistTask.is_starred) == True

def create_list(*, db_session, list_in: TodolistCreate) -> Todolist:
    """Creates a Todolist"""
    todolist = Todolist(
        **list_in.model_dump()
    )
    
    db_session.add(todolist)
    db_session.commit()
    db_session.refresh(todolist)

    return todolist

def create_task(*, db_session, task_in: TodotaskCreate) -> TodolistTask:
    """Creates a task and adds it to a Todolist"""
    task = TodolistTask(
        **task_in.model_dump()
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    return task
# def get_task_count(db_session: DbSession, list_id: int):
#     stmt = select(func.count()).where(TodolistTask.list_id == list_id)
#     return db_session.scalar(stmt)
