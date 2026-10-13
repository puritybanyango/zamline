# Owner: Purity Anyango
# Feature: Fleet Management

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.trucks import AvailabilityStatus, BodyType


class TruckCreate(BaseModel):
    plate_number: str = Field(min_length=2, max_length=20)
    truck_type: str = Field(min_length=2, max_length=30)
    body_type: BodyType
    capacity_kg: float = Field(gt=0)
    fuel_consumption_l_per_100km: float = Field(gt=0)
    maintenance_per_km: Decimal = Field(gt=0)
    current_location: str | None = Field(default=None, max_length=50)
    available_from: datetime | None = None


class TruckUpdate(BaseModel):
    truck_type: str | None = Field(default=None, min_length=2, max_length=30)
    body_type: BodyType | None = None
    capacity_kg: float | None = Field(default=None, gt=0)
    fuel_consumption_l_per_100km: float | None = Field(default=None, gt=0)
    maintenance_per_km: Decimal | None = Field(default=None, gt=0)
    availability_status: AvailabilityStatus | None = None
    current_location: str | None = Field(default=None, max_length=50)
    available_from: datetime | None = None


class TruckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    truck_id: UUID
    company_id: UUID
    plate_number: str
    truck_type: str
    body_type: BodyType
    capacity_kg: float
    fuel_consumption_l_per_100km: float
    maintenance_per_km: Decimal
    availability_status: AvailabilityStatus
    current_location: str | None
    available_from: datetime | None
