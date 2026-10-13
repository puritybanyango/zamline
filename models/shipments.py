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
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.trucks import BodyType


class ShipmentStatus(str, enum.Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.company_id"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True
    )
    origin_address = Column(String(250), nullable=False)
    origin_latitude = Column(Numeric(9, 6, asdecimal=False), nullable=False)
    origin_longitude = Column(Numeric(9, 6, asdecimal=False), nullable=False)
    destination_address = Column(String(250), nullable=False)
    destination_latitude = Column(Numeric(9, 6, asdecimal=False), nullable=False)
    destination_longitude = Column(Numeric(9, 6, asdecimal=False), nullable=False)
    cargo_type = Column(String(20), nullable=False)
    weight_kg = Column(Float, nullable=False)
    required_body_type = Column(
        Enum(
            BodyType,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="bodytype",
        ),
        nullable=False,
    )
    pickup_time = Column(DateTime(timezone=True), nullable=False)
    special_requirements = Column(Text, nullable=True)
    proposed_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(
        Enum(
            ShipmentStatus,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="shipmentstatus",
        ),
        nullable=False,
        default=ShipmentStatus.OPEN,
        server_default=ShipmentStatus.OPEN.value,
    )
    published_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "origin_latitude BETWEEN -90 AND 90", name="ck_shipments_origin_lat"
        ),
        CheckConstraint(
            "origin_longitude BETWEEN -180 AND 180", name="ck_shipments_origin_lng"
        ),
        CheckConstraint(
            "destination_latitude BETWEEN -90 AND 90", name="ck_shipments_dest_lat"
        ),
        CheckConstraint(
            "destination_longitude BETWEEN -180 AND 180", name="ck_shipments_dest_lng"
        ),
        CheckConstraint("weight_kg > 0", name="ck_shipments_weight_positive"),
        CheckConstraint("proposed_amount > 0", name="ck_shipments_amount_positive"),
        Index("ix_shipments_status", "status"),
        Index("ix_shipments_required_body_type", "required_body_type"),
    )

    company = relationship("Company", back_populates="shipments")
    user = relationship("User", back_populates="shipments")
    matches = relationship(
        "ShipmentMatch", back_populates="shipment", cascade="all, delete-orphan"
    )
    reservation = relationship("Reservation", back_populates="shipment", uselist=False)
