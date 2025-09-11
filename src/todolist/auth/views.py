import logging

from fastapi import APIRouter

from pydantic import ValidationError

from .models import (
    UserCreate,
    ToDoListUser,
    UserInfo
)
from .service import (
    get,
    create,
    get_current_user,
    get_by_email,
    get_or_create
)

from todolist.database.core import DbSession
from todolist.auth.service import CurrentUser

auth_router = APIRouter()
user_router = APIRouter()

@user_router.post(
    "",
    response_model=UserInfo
)
def create_user(
    user_in: UserCreate,
    db_session: DbSession,
    current_user: CurrentUser
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user:
        raise ValidationError(
            [
                {
                    "msg": "A user with this email already exists.",
                    "loc": "email",
                }
            ]
        )