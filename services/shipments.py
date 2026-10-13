# Owner: Sandra Twala
# Feature: Shipment Management and Cargo Validation

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import UNACCEPTED_CARGO_TYPES
from models.shipments import ShipmentStatus
from repositories.shipments import (
    create_shipment as create_shipment_record,
    get_company_shipment,
    list_company_shipments,
)
from schemas.shipments import ShipmentCreate
from services.audit_logs import record_event


def validate_cargo(cargo_type: str) -> None:
    if cargo_type.strip().lower() in UNACCEPTED_CARGO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="This cargo type is not accepted in the ZamLine MVP",
        )


def create_shipment(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    data: ShipmentCreate,
):
    validate_cargo(data.cargo_type)

    shipment = create_shipment_record(
        db,
        company_id=company_id,
        user_id=user_id,
        **data.model_dump(),
    )
    record_event(
        db,
        "shipment_published",
        user_id=user_id,
        company_id=company_id,
        entity_type="shipment",
        entity_id=shipment.shipment_id,
    )
    db.commit()
    db.refresh(shipment)
    return shipment


def list_shipments(db: Session, company_id: UUID):
    return list_company_shipments(db, company_id)


def get_shipment(db: Session, company_id: UUID, shipment_id: UUID):
    shipment = get_company_shipment(db, company_id, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


def cancel_shipment(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    shipment_id: UUID,
):
    shipment = get_shipment(db, company_id, shipment_id)
    if shipment.status != ShipmentStatus.OPEN:
        raise HTTPException(
            status_code=409,
            detail="Only open shipments can be cancelled",
        )

    shipment.status = ShipmentStatus.CANCELLED
    record_event(
        db,
        "shipment_cancelled",
        user_id=user_id,
        company_id=company_id,
        entity_type="shipment",
        entity_id=shipment.shipment_id,
    )
    db.commit()
    db.refresh(shipment)
    return shipment
