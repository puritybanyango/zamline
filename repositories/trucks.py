# Owner: Purity Anyango
# Feature: Fleet Management

from uuid import UUID

from sqlalchemy.orm import Session

from models.trucks import AvailabilityStatus, Truck


def create_truck(db: Session, **values):
    truck = Truck(**values)
    db.add(truck)
    db.flush()
    return truck


def get_truck_by_id(db: Session, truck_id: UUID):
    return db.query(Truck).filter(Truck.truck_id == truck_id).first()


def get_company_truck(db: Session, company_id: UUID, truck_id: UUID):
    return (
        db.query(Truck)
        .filter(Truck.company_id == company_id, Truck.truck_id == truck_id)
        .first()
    )


def list_company_trucks(db: Session, company_id: UUID):
    return db.query(Truck).filter(Truck.company_id == company_id).all()


def list_available_company_trucks(db: Session, company_id: UUID):
    return (
        db.query(Truck)
        .filter(
            Truck.company_id == company_id,
            Truck.availability_status == AvailabilityStatus.AVAILABLE,
        )
        .all()
    )
