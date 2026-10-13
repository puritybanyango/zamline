from typing import Optional, Union
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import get_current_company, get_current_user
from schemas.companies import CompanyResponse, CompanyVerificationSubmit
from services.companies import submit_verification

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/me", response_model=CompanyResponse)
def read_my_company(company=Depends(get_current_company)):
    return company


@router.post("/me/verification", response_model=CompanyResponse)
def submit_my_verification(
    payload: CompanyVerificationSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return submit_verification(
        db,
        current_user.company_id,
        current_user.user_id,
        str(payload.certificate_file_url),
    )
