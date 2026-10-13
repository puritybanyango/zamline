# Owner: Shamy Umukundwa
# Feature: Acceptance, Reservation and Contact Handoff

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.reservations import ReservationStatus


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: UUID
    shipment_id: UUID
    company_id: UUID
    truck_id: UUID
    user_id: UUID
    match_id: UUID
    status: ReservationStatus
    reserved_at: datetime


class ContactHandoffResponse(BaseModel):
    business_name: str
    company_email: str
    phone_number: str
