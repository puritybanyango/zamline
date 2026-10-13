# Owner: Helen Mezgebe
# Feature: PACRA Business Verification

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.companies import VerificationStatus
from repositories.companies import get_company_by_id
from services.audit_logs import record_event


def get_company(db: Session, company_id: UUID):
    company = get_company_by_id(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def submit_verification(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    certificate_file_url: str,
):
    company = get_company(db, company_id)
    company.certificate_file_url = certificate_file_url
    company.verification_status = VerificationStatus.PENDING
    company.verified_at = None
    company.verification_failure_reason = None

    record_event(
        db,
        "verification_submitted",
        user_id=user_id,
        company_id=company_id,
        entity_type="company",
        entity_id=company_id,
    )
    db.commit()
    db.refresh(company)
    return company


def record_verification_result(
    db: Session,
    company_id: UUID,
    status: VerificationStatus,
    failure_reason: str | None = None,
    details: dict | None = None,
):
    company = get_company(db, company_id)

    if status == VerificationStatus.VERIFIED:
        company.verified_at = datetime.now(timezone.utc)
        company.verification_failure_reason = None
    else:
        company.verified_at = None
        company.verification_failure_reason = failure_reason

    company.verification_status = status

    record_event(
        db,
        "verification_completed",
        company_id=company_id,
        entity_type="company",
        entity_id=company_id,
        details={
            "status": status.value,
            "failure_reason": failure_reason,
            **(details or {}),
        },
    )
    db.commit()
    db.refresh(company)
    return company
