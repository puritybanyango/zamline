# Owner: Purity Anyango
# Feature: Fleet Management

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.trucks import Truck
from repositories.trucks import (
    create_truck as create_truck_record,
    get_company_truck,
    list_company_trucks,
)
from schemas.trucks import TruckCreate, TruckUpdate
from services.audit_logs import record_event


def create_truck(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    data: TruckCreate,
):
    try:
        truck = create_truck_record(
            db,
            company_id=company_id,
            **data.model_dump(),
        )
        record_event(
            db,
            "truck_created",
            user_id=user_id,
            company_id=company_id,
            entity_type="truck",
            entity_id=truck.truck_id,
        )
        db.commit()
        db.refresh(truck)
        return truck
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Truck registration already exists")


def list_trucks(db: Session, company_id: UUID):
    return list_company_trucks(db, company_id)


def get_truck(db: Session, company_id: UUID, truck_id: UUID):
    truck = get_company_truck(db, company_id, truck_id)
    if truck is None:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


def update_truck(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    truck_id: UUID,
    data: TruckUpdate,
):
    truck: Truck = get_truck(db, company_id, truck_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(truck, field, value)

    record_event(
        db,
        "truck_updated",
        user_id=user_id,
        company_id=company_id,
        entity_type="truck",
        entity_id=truck.truck_id,
        details={"updated_fields": list(data.model_dump(exclude_unset=True).keys())},
    )
    db.commit()
    db.refresh(truck)
    return truck
