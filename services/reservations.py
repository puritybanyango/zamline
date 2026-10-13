# Owner: Shamy Umukundwa
# Feature: Acceptance, Reservation and Contact Handoff

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.reservations import ReservationStatus
from repositories.companies import get_company_by_id
from repositories.reservations import get_reservation_by_id
from repositories.shipments import get_company_shipment
from services.audit_logs import record_event


def get_reservation(db: Session, company_id: UUID, reservation_id: UUID):
    reservation = get_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    is_fleet_party = reservation.company_id == company_id
    is_shipper_party = (
        get_company_shipment(db, company_id, reservation.shipment_id) is not None
    )

    if not is_fleet_party and not is_shipper_party:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return reservation


def get_contact_handoff(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    reservation_id: UUID,
):
    reservation = get_reservation(db, company_id, reservation_id)
    if reservation.status != ReservationStatus.ACCEPTED:
        raise HTTPException(status_code=403, detail="Contact handoff is not available")

    shipment = reservation.shipment

    if reservation.company_id == company_id:
        other_company_id = shipment.company_id
    elif shipment.company_id == company_id:
        other_company_id = reservation.company_id
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")

    other_company = get_company_by_id(db, other_company_id)
    if other_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    record_event(
        db,
        "contact_viewed",
        user_id=user_id,
        company_id=company_id,
        entity_type="reservation",
        entity_id=reservation.reservation_id,
    )
    db.commit()

    return {
        "business_name": other_company.business_name,
        "company_email": other_company.company_email,
        "phone_number": other_company.phone_number,
    }
