# Owner: Sandra Twala
# Feature: Shipment Management and Cargo Validation

from uuid import UUID

from sqlalchemy.orm import Session

from models.companies import VerificationStatus
from models.shipments import Shipment, ShipmentStatus


def create_shipment(db: Session, **values):
    shipment = Shipment(**values)
    db.add(shipment)
    db.flush()
    return shipment


def get_company_shipment(db: Session, company_id: UUID, shipment_id: UUID):
    return (
        db.query(Shipment)
        .filter(
            Shipment.company_id == company_id,
            Shipment.shipment_id == shipment_id,
        )
        .first()
    )


def list_company_shipments(db: Session, company_id: UUID):
    return (
        db.query(Shipment)
        .filter(Shipment.company_id == company_id)
        .order_by(Shipment.published_at.desc())
        .all()
    )


def list_open_verified_shipments(db: Session):
    from models.companies import Company

    return (
        db.query(Shipment)
        .join(Company, Shipment.company_id == Company.company_id)
        .filter(
            Shipment.status == ShipmentStatus.OPEN,
            Company.verification_status == VerificationStatus.VERIFIED,
        )
        .all()
    )
