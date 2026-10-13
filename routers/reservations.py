# Owner: Shamy Umukundwa
# Feature: Acceptance, Reservation and Contact Handoff

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import get_current_user
from schemas.reservations import ContactHandoffResponse, ReservationResponse
from services.reservations import get_contact_handoff, get_reservation

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/{reservation_id}", response_model=ReservationResponse)
def read(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_reservation(db, current_user.company_id, reservation_id)


@router.get("/{reservation_id}/contact", response_model=ContactHandoffResponse)
def contact(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_contact_handoff(
        db,
        current_user.company_id,
        current_user.user_id,
        reservation_id,
    )
