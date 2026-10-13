# Owner: Jesca Amondi
# Feature: Cost Estimation and Margin Decision Support

from uuid import UUID

from sqlalchemy.orm import Session

from models.shipment_matches import ShipmentMatch
from models.trucks import Truck


def get_fleet_match(db: Session, company_id: UUID, match_id: UUID):
    return (
        db.query(ShipmentMatch)
        .join(Truck, ShipmentMatch.truck_id == Truck.truck_id)
        .filter(
            ShipmentMatch.match_id == match_id,
            Truck.company_id == company_id,
        )
        .first()
    )
