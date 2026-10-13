# Owner: Purity Anyango
# Feature: Private Operating Cost Settings

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.companies import CompanyType
from repositories.cost_settings import get_cost_settings_company
from schemas.cost_settings import CostSettingsUpdate
from services.audit_logs import record_event


def get_cost_settings(db: Session, company_id: UUID):
    company = get_cost_settings_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.company_type != CompanyType.FLEET:
        raise HTTPException(status_code=403, detail="Fleet company required")
    return company


def update_cost_settings(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    data: CostSettingsUpdate,
):
    company = get_cost_settings(db, company_id)
    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(company, field, value)

    record_event(
        db,
        "cost_settings_updated",
        user_id=user_id,
        company_id=company_id,
        entity_type="company",
        entity_id=company_id,
        details={"updated_fields": list(updates.keys())},
    )
    db.commit()
    db.refresh(company)
    return company
