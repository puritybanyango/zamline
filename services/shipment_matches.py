# Owner: Shamy Umukundwa
# Feature: Fleet Matching and Acceptance

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.shipment_matches import ManagerDecision, ShipmentMatch
from models.shipments import Shipment, ShipmentStatus
from models.trucks import AvailabilityStatus
from repositories.reservations import (
    create_reservation,
    get_reservation_by_shipment,
)
from repositories.shipment_matches import (
    create_match,
    find_match,
    get_company_match,
    get_company_match_for_update,
    list_company_matches,
)
from repositories.shipments import list_open_verified_shipments
from repositories.trucks import list_available_company_trucks
from services.audit_logs import record_event


def _compatible(shipment: Shipment, truck) -> bool:
    return (
        truck.availability_status == AvailabilityStatus.AVAILABLE
        and truck.capacity_kg >= shipment.weight_kg
        and truck.body_type == shipment.required_body_type
    )


def refresh_matches(
    db: Session,
    company_id: UUID,
    user_id: UUID,
) -> int:
    shipments = list_open_verified_shipments(db)
    trucks = list_available_company_trucks(db, company_id)
    created = 0

    for shipment in shipments:
        if shipment.company_id == company_id:
            continue

        for truck in trucks:
            if not _compatible(shipment, truck):
                continue
            if find_match(db, shipment.shipment_id, truck.truck_id):
                continue

            match = create_match(db, shipment.shipment_id, truck.truck_id)
            record_event(
                db,
                "match_created",
                user_id=user_id,
                company_id=company_id,
                entity_type="shipment_match",
                entity_id=match.match_id,
                details={
                    "shipment_id": str(shipment.shipment_id),
                    "truck_id": str(truck.truck_id),
                },
            )
            created += 1

    db.commit()
    return created


def list_matches(db: Session, company_id: UUID):
    return list_company_matches(db, company_id)


def get_match(db: Session, company_id: UUID, match_id: UUID):
    match = get_company_match(db, company_id, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


def decide_match(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    match_id: UUID,
    decision: ManagerDecision,
):
    if decision not in {ManagerDecision.ACCEPTED, ManagerDecision.DECLINED}:
        raise HTTPException(
            status_code=400,
            detail="Decision must be accepted or declined",
        )

    if decision == ManagerDecision.DECLINED:
        match = get_match(db, company_id, match_id)
        if match.manager_decision != ManagerDecision.PENDING:
            raise HTTPException(
                status_code=409,
                detail="Match has already been decided",
            )

        match.manager_decision = ManagerDecision.DECLINED
        match.user_id = user_id
        match.decided_at = datetime.now(timezone.utc)
        record_event(
            db,
            "shipment_declined",
            user_id=user_id,
            company_id=company_id,
            entity_type="shipment_match",
            entity_id=match.match_id,
        )
        db.commit()
        db.refresh(match)
        return match

    try:
        match = get_company_match_for_update(db, company_id, match_id)
        if match is None:
            raise HTTPException(status_code=404, detail="Match not found")

        shipment = (
            db.query(Shipment)
            .filter(Shipment.shipment_id == match.shipment_id)
            .with_for_update()
            .first()
        )
        if shipment is None:
            raise HTTPException(status_code=404, detail="Shipment not found")

        if match.manager_decision != ManagerDecision.PENDING:
            raise HTTPException(
                status_code=409,
                detail="Match has already been decided",
            )

        if shipment.status != ShipmentStatus.OPEN:
            raise HTTPException(
                status_code=409,
                detail="Shipment is no longer available",
            )

        if get_reservation_by_shipment(db, shipment.shipment_id):
            raise HTTPException(status_code=409, detail="Shipment is already reserved")

        if not _compatible(shipment, match.truck):
            raise HTTPException(
                status_code=409,
                detail="Truck is no longer compatible or available",
            )

        match.manager_decision = ManagerDecision.ACCEPTED
        match.user_id = user_id
        match.decided_at = datetime.now(timezone.utc)

        reservation = create_reservation(
            db,
            shipment_id=shipment.shipment_id,
            company_id=company_id,
            truck_id=match.truck_id,
            user_id=user_id,
            match_id=match.match_id,
        )

        shipment.status = ShipmentStatus.CONFIRMED
        match.truck.availability_status = AvailabilityStatus.UNAVAILABLE

        (
            db.query(ShipmentMatch)
            .filter(
                ShipmentMatch.shipment_id == shipment.shipment_id,
                ShipmentMatch.match_id != match.match_id,
                ShipmentMatch.manager_decision == ManagerDecision.PENDING,
            )
            .update(
                {
                    ShipmentMatch.manager_decision: ManagerDecision.CLOSED,
                    ShipmentMatch.decided_at: datetime.now(timezone.utc),
                },
                synchronize_session=False,
            )
        )

        record_event(
            db,
            "shipment_accepted",
            user_id=user_id,
            company_id=company_id,
            entity_type="shipment_match",
            entity_id=match.match_id,
        )
        record_event(
            db,
            "reservation_created",
            user_id=user_id,
            company_id=company_id,
            entity_type="reservation",
            entity_id=reservation.reservation_id,
        )

        db.commit()
        db.refresh(match)
        return match
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Shipment was secured by another fleet",
        )
