import bcrypt
import logging

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from pydantic import ValidationError

from .models import (
    UserCreate,
    TodolistUser,
    UserInfo,
    UserLogin,
    UserAuthResponse,
    OtpCode,
    OtpModel,
    UserPasswordReset
)

from .service import (
    get,
    create,
    get_current_user,
    get_by_email,
    get_or_create,
    send_otp_user
)

from todolist.database.core import DbSession
from todolist.auth.service import CurrentUser


log = logging.getLogger(__name__)

auth_router = APIRouter()

@auth_router.post(
    "/register"
)

def register(
    user_in: UserCreate,
    db_session: DbSession,
    background_tasks: BackgroundTasks
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                    {
                    "msg": "A user with this email already exists.",
                    "loc": "email",
                }
            ]
        )
    user = create(db_session=db_session, user_in=user_in)

    #send otp to user mail after creation for verification
    try:
        send_otp_user(
            db_session=db_session, user=user, background_tasks=background_tasks
        )
    except Exception as e:
        log.error(f"User created but failed to send OTP email")
        user.is_verified = False

        db_session.commit()

    return JSONResponse({"detail":"User registered successfully, Please verify via OTP"},
        status_code=status.HTTP_201_CREATED)


@auth_router.post("/verify_email")

def verify_email(
    db_session: DbSession, 
    user_in: UserCreate,
    otp_in: OtpCode
):
    """verify otp by comparing saved otp"""
    user = get_by_email(db_session=db_session, user_id=user_in.email)

    otp_instance = db_session.query(OtpModel).filter(OtpModel.user_id == user.id).first()

    if not user or not otp_instance:
        raise HTTPException(status_code=400, detail="User or OTP not found")
    
    otp_code = otp_in.otp_code #input otp

    #Check OTP Validity
    if otp_instance.otp_code == otp_code and otp_instance.otp_expires > datetime.now(timezone.utc):
        user.is_verified = True
        db_session.delete(otp_instance)
        db_session.commit()

        return JSONResponse({"detail":"Email verified successfully, Proceed to login"},
            status_code=status.HTTP_201_CREATED)
    
    raise HTTPException(status_code=400, detail="Invalid or expired OTP")

@auth_router.post("/resend-otp")

def resend_otp(db_session: DbSession, user_in: UserCreate, background_tasks: BackgroundTasks):
    """This endpoint resends otp if it expires"""

    user = get_by_email(db_session=db_session, email=user_in.email)
    if user.is_verified:
        return JSONResponse(
                {"detail": "User has already been verified. please proceed to login"},
                status=status.HTTP_200_OK,
            )
    otp_instance = db_session.query(OtpModel).filter(OtpModel.user_id == user.id).first()

    if otp_instance and otp_instance.otp_expires > datetime.now(timezone.utc):
        return JSONResponse(
                {"detail": "An OTP has already been sent and is still valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    send_otp_user(
            db_session=db_session, user=user, background_tasks=background_tasks
        )

    return JSONResponse({"detail":"OTP resent successfully, Please verify via OTP"},
        status_code=status.HTTP_201_CREATED)


@auth_router.post(
    "/login",
    response_model=UserAuthResponse
)

def login(
    user_in: UserLogin,
    db_session: DbSession
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user and user.verify_password(user_in.password):
        return {"detail":"User logged in successfully","token":user.token}
    
    return JSONResponse(
        content={"detail":"Invalid email or password"},
        status_code=status.HTTP_401_UNAUTHORIZED
    )
    
# @auth_router.post(
#     "/logout"
# )

# def logout(db_session: DbSession):
#     user = get_by_email(db_session=db_session, email) TODO implement logout

@auth_router.post("/forgot-password")

def forgot_password(db_session: DbSession, user_in: UserCreate, background_tasks: BackgroundTasks):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this email does not exist."}],
        )

    send_otp_user(
            db_session=db_session, user=user, background_tasks=background_tasks
        )
    
    return JSONResponse(
            {
                "message": "Otp has been sent to your email, please clease check your inbox to reset your password."
            },
            status=status.HTTP_200_OK,
        )


@auth_router.post("/reset-password")

def reset_password(
    db_session: DbSession,
    password_reset: UserPasswordReset,
    user_in: UserCreate,
    otp_in: OtpCode
):
    """User endpoint to reset user password"""
    user = get_by_email(db_session=db_session, email=user_in.email)
    otp_instance = db_session.query(OtpModel).filter(OtpModel.user_id == user.id).first()

    if not user or not otp_instance:
        raise HTTPException(status_code=400, detail="User or OTP not found")
    
    otp_code = otp_in.otp_code #input otp

    #Check OTP Validity
    if otp_instance.otp_code == otp_code and otp_instance.otp_expires > datetime.now(timezone.utc):
        try:
            user.set_password(password_reset.new_password)
            db_session.commit()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[{"msg": str(e)}],
            ) from e
    return user