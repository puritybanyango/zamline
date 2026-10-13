# Owner: Purity Anyango
# Feature: Private Operating Cost Settings

from uuid import UUID

from sqlalchemy.orm import Session

from models.companies import Company


def get_cost_settings_company(db: Session, company_id: UUID):
    return db.query(Company).filter(Company.company_id == company_id).first()
