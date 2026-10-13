# Owner: Shamy Umukundwa
# Feature: Acceptance, Reservation and Contact Handoff

from uuid import UUID

from sqlalchemy.orm import Session

from models.reservations import Reservation


def create_reservation(db: Session, **values):
    reservation = Reservation(**values)
    db.add(reservation)
    db.flush()
    return reservation


def get_reservation_by_shipment(db: Session, shipment_id: UUID):
    return db.query(Reservation).filter(Reservation.shipment_id == shipment_id).first()


def get_reservation_by_id(db: Session, reservation_id: UUID):
    return (
        db.query(Reservation)
        .filter(Reservation.reservation_id == reservation_id)
        .first()
    )
