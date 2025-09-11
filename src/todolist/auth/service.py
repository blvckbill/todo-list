import logging

from fastapi import HTTPException, Depends
from fastapi.security.utils import get_authorization_scheme_param

from jose import jwt, JWTError
from jose.exceptions import JWKError

from sqlalchemy.exc import IntegrityError

from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from todolist.auth.models import ToDoListUser, UserCreate
from todolist.config import TODOLIST_JWT_SECRET, TODOLIST_JWT_ALG

from typing import Annotated

log = logging.getLogger(__name__)


def get(*, db_session, user_id: int) -> ToDoListUser | None:
    """Returns a user based on the given user id."""
    return db_session.query(ToDoListUser).filter(ToDoListUser.id == user_id).one_or_none()


def get_by_email(*, db_session, email: str) -> ToDoListUser| None:
    """Returns a user based on the given email"""
    return db_session.query(ToDoListUser).filter(ToDoListUser.email == email).one_or_none()


def create(*, db_session, user_in: UserCreate) -> ToDoListUser:
    """Creates a new TodoList User"""

    user = ToDoListUser(
        **user_in.model_dump(exclude={"password"}),
        password=user_in.password
    )

    db_session.add(user)
    db_session.commit()

    return user


def get_or_create(*, db_session, user_in: UserCreate) -> ToDoListUser:
    """Gets an existing user or creates a new one."""
    user = get_by_email(db_session=db_session, email=user_in.email)

    if not user:
        try:
            user = create(db_session=db_session, user_in=user_in)
        except IntegrityError:
            db_session.rollback()
            log.exception(f"Unable to create user with email address {user_in.email}.")

    return user


             
def get_current_user(request: Request)-> ToDoListUser:
    """Attempts to get the current authenticated user"""
    authorization = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        log.exception(
            f"Malformed authorization header. Scheme: {scheme} Param: {param} Authorization: {authorization}"
        )
        return
    token = param

    try:
        data = jwt.decode(token, TODOLIST_JWT_SECRET, algorithms=TODOLIST_JWT_ALG)
    except (JWTError, JWKError):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=[{"msg": "Could not validate credentials"}],
        ) from None
    
    user_id = data.get("sub")

    user = get(
        db_session=request.state.db,
        user_id=user_id
    )
    return user

CurrentUser = Annotated[ToDoListUser, Depends(get_current_user)]