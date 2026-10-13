# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.users import (
    EmailRequest,
    LoginRequest,
    OtpVerifyRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from services.users import login_user, register_user, resend_otp, verify_user_otp

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, payload)
    return RegisterResponse(
        user=UserResponse.model_validate(user),
        message="Registration created. Verify the email code to activate the account.",
    )


@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(payload: OtpVerifyRequest, db: Session = Depends(get_db)):
    return verify_user_otp(db, str(payload.email), payload.code)


@router.post("/resend-otp", status_code=status.HTTP_204_NO_CONTENT)
def resend(payload: EmailRequest, db: Session = Depends(get_db)):
    resend_otp(db, str(payload.email))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, str(payload.email), payload.password)
    return TokenResponse(access_token=token)
