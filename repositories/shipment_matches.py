# Owner: Shamy Umukundwa
# Feature: Fleet Matching and Acceptance

from uuid import UUID

from sqlalchemy.orm import Session

from models.shipment_matches import ShipmentMatch
from models.trucks import Truck


def get_match_by_id(db: Session, match_id: UUID):
    return db.query(ShipmentMatch).filter(ShipmentMatch.match_id == match_id).first()


def get_company_match(db: Session, company_id: UUID, match_id: UUID):
    return (
        db.query(ShipmentMatch)
        .join(Truck, ShipmentMatch.truck_id == Truck.truck_id)
        .filter(
            ShipmentMatch.match_id == match_id,
            Truck.company_id == company_id,
        )
        .first()
    )


def get_company_match_for_update(db: Session, company_id: UUID, match_id: UUID):
    return (
        db.query(ShipmentMatch)
        .join(Truck, ShipmentMatch.truck_id == Truck.truck_id)
        .filter(
            ShipmentMatch.match_id == match_id,
            Truck.company_id == company_id,
        )
        .with_for_update()
        .first()
    )


def list_company_matches(db: Session, company_id: UUID):
    return (
        db.query(ShipmentMatch)
        .join(Truck, ShipmentMatch.truck_id == Truck.truck_id)
        .filter(Truck.company_id == company_id)
        .order_by(ShipmentMatch.created_at.desc())
        .all()
    )


def find_match(db: Session, shipment_id: UUID, truck_id: UUID):
    return (
        db.query(ShipmentMatch)
        .filter(
            ShipmentMatch.shipment_id == shipment_id,
            ShipmentMatch.truck_id == truck_id,
        )
        .first()
    )


def create_match(db: Session, shipment_id: UUID, truck_id: UUID):
    match = ShipmentMatch(shipment_id=shipment_id, truck_id=truck_id)
    db.add(match)
    db.flush()
    return match
