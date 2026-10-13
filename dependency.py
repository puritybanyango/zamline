# Owner: Shared Team
# Feature: Authentication and authorization dependencies

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models.companies import VerificationStatus
from models.users import UserRole
from repositories.companies import get_company_by_id
from repositories.users import get_user_by_id
from security.tokens import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError, jwt.PyJWTError, RuntimeError):
        raise credentials_error

    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_error

    return user


def get_current_company(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = get_company_by_id(db, current_user.company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def require_role(*allowed_roles: UserRole):
    def role_dependency(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return role_dependency


def require_verified_company(
    company=Depends(get_current_company),
):
    if company.verification_status != VerificationStatus.VERIFIED:
        raise HTTPException(status_code=403, detail="Company is not verified")
    return company
