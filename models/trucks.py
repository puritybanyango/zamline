from database import Base
import uuid
import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class BodyType(str, enum.Enum):
    FLATBED = "flatbed"
    BOX = "box"
    TANKER = "tanker"
    REFRIGERATED = "refrigerated"
    TIPPER = "tipper"
    CONTAINER = "container"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class Truck(Base):
    __tablename__ = "trucks"

    truck_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.company_id"),
        nullable=False,
        index=True,
    )
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    truck_type = Column(String(30), nullable=False)
    body_type = Column(
        Enum(
            BodyType,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="bodytype",
        ),
        nullable=False,
    )
    capacity_kg = Column(Float, nullable=False)
    fuel_consumption_l_per_100km = Column(Float, nullable=False)
    maintenance_per_km = Column(Numeric(10, 2), nullable=False)
    availability_status = Column(
        Enum(
            AvailabilityStatus,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="availabilitystatus",
        ),
        nullable=False,
        default=AvailabilityStatus.AVAILABLE,
        server_default=AvailabilityStatus.AVAILABLE.value,
    )
    current_location = Column(String(50), nullable=True)
    available_from = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("capacity_kg > 0", name="ck_trucks_capacity_positive"),
        CheckConstraint(
            "fuel_consumption_l_per_100km > 0",
            name="ck_trucks_fuel_consumption_positive",
        ),
        Index("ix_trucks_availability_status", "availability_status"),
        Index("ix_trucks_body_type", "body_type"),
    )

    company = relationship("Company", back_populates="trucks")
    shipment_matches = relationship("ShipmentMatch", back_populates="truck")
    reservations = relationship("Reservation", back_populates="truck")
