# Owner: Sandra Twala
# Feature: Shipment Management and Cargo Validation

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.shipments import ShipmentStatus
from models.trucks import BodyType


class ShipmentCreate(BaseModel):
    origin_address: str = Field(min_length=2, max_length=250)
    origin_latitude: float = Field(ge=-90, le=90)
    origin_longitude: float = Field(ge=-180, le=180)
    destination_address: str = Field(min_length=2, max_length=250)
    destination_latitude: float = Field(ge=-90, le=90)
    destination_longitude: float = Field(ge=-180, le=180)
    cargo_type: str = Field(min_length=2, max_length=20)
    weight_kg: float = Field(gt=0)
    required_body_type: BodyType
    pickup_time: datetime
    special_requirements: str | None = None
    proposed_amount: Decimal = Field(gt=0)


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipment_id: UUID
    company_id: UUID
    user_id: UUID
    origin_address: str
    origin_latitude: float
    origin_longitude: float
    destination_address: str
    destination_latitude: float
    destination_longitude: float
    cargo_type: str
    weight_kg: float
    required_body_type: BodyType
    pickup_time: datetime
    special_requirements: str | None
    proposed_amount: Decimal
    status: ShipmentStatus
    published_at: datetime
