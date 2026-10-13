# Owner: Jesca Amondi
# Feature: Route Information

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from integrations.openrouteservice import OpenRouteServiceError, get_hgv_route
from repositories.cost_estimation import get_fleet_match


def get_route_for_match(db: Session, company_id: UUID, match_id: UUID) -> dict:
    match = get_fleet_match(db, company_id, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    shipment = match.shipment

    try:
        return get_hgv_route(
            float(shipment.origin_latitude),
            float(shipment.origin_longitude),
            float(shipment.destination_latitude),
            float(shipment.destination_longitude),
        )
    except OpenRouteServiceError as error:
        raise HTTPException(status_code=502, detail=str(error))
