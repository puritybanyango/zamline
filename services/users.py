# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.companies import CompanyType
from models.users import UserRole
from repositories.companies import (
    create_company,
    get_company_by_email,
    get_company_by_registration_number,
)
from repositories.users import create_user, get_user_by_email
from schemas.users import RegisterRequest
from security.otp import otp_store
from security.passwords import hash_password, verify_password
from security.tokens import create_access_token
from services.audit_logs import record_event
from services.email_service import send_otp_email


def _validate_company_role(company_type: CompanyType, role: UserRole) -> None:
    valid = (company_type == CompanyType.SHIPPER and role == UserRole.SHIPPER) or (
        company_type == CompanyType.FLEET and role == UserRole.FLEET_MANAGER
    )
    if not valid:
        raise HTTPException(
            status_code=400,
            detail="User role does not match the selected company type",
        )


def register_user(db: Session, data: RegisterRequest):
    _validate_company_role(data.company_type, data.role)

    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email is already registered")
    if get_company_by_registration_number(db, data.registration_number):
        raise HTTPException(
            status_code=409,
            detail="Registration number is already registered",
        )
    if get_company_by_email(db, data.company_email):
        raise HTTPException(
            status_code=409,
            detail="Company email is already registered",
        )

    user = None
    try:
        company = create_company(
            db,
            company_type=data.company_type,
            business_name=data.business_name.strip(),
            registration_number=data.registration_number,
            company_email=str(data.company_email).lower(),
            phone_number=data.phone_number.strip(),
        )
        user = create_user(
            db,
            company_id=company.company_id,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=str(data.email).lower(),
            password_hash=hash_password(data.password),
            role=data.role,
            is_active=False,
        )
        record_event(
            db,
            "user_registered",
            user_id=user.user_id,
            company_id=company.company_id,
            entity_type="user",
            entity_id=user.user_id,
        )

        code = otp_store.issue(user.user_id)
        send_otp_email(user.email, code)

        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        if user is not None:
            otp_store.invalidate(user.user_id)
        raise HTTPException(status_code=409, detail="Registration data already exists")
    except RuntimeError as error:
        db.rollback()
        if user is not None:
            otp_store.invalidate(user.user_id)
        raise HTTPException(status_code=503, detail=str(error))


def resend_otp(db: Session, email: str) -> None:
    user = get_user_by_email(db, email)
    if user is None:
        return

    code = otp_store.issue(user.user_id)
    try:
        send_otp_email(user.email, code)
    except RuntimeError as error:
        otp_store.invalidate(user.user_id)
        raise HTTPException(status_code=503, detail=str(error))


def verify_user_otp(db: Session, email: str, code: str):
    user = get_user_by_email(db, email)
    if user is None or not otp_store.verify(user.user_id, code):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code",
        )

    user.is_active = True
    record_event(
        db,
        "email_verified",
        user_id=user.user_id,
        company_id=user.company_id,
        entity_type="user",
        entity_id=user.user_id,
    )
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> str:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        if user is not None:
            record_event(
                db,
                "login_failed",
                user_id=user.user_id,
                company_id=user.company_id,
                entity_type="user",
                entity_id=user.user_id,
            )
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Email verification is required")

    record_event(
        db,
        "login_success",
        user_id=user.user_id,
        company_id=user.company_id,
        entity_type="user",
        entity_id=user.user_id,
    )
    db.commit()

    try:
        return create_access_token(
            user.user_id,
            user.company_id,
            user.role.value,
        )
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured",
        )
