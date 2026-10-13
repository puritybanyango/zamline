# Owner: Helen Mezgebe
# Feature: PACRA Business Verification


from uuid import UUID

from sqlalchemy.orm import Session

from models.companies import Company


def get_company_by_id(db: Session, company_id: UUID):
    return db.query(Company).filter(Company.company_id == company_id).first()


def get_company_by_registration_number(db: Session, registration_number: str):
    return (
        db.query(Company)
        .filter(Company.registration_number == registration_number)
        .first()
    )


def get_company_by_email(db: Session, company_email: str):
    return (
        db.query(Company).filter(Company.company_email == company_email.lower()).first()
    )


def create_company(db: Session, **values):
    company = Company(**values)
    db.add(company)
    db.flush()
    return company
