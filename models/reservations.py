from database import Base
import uuid
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ReservationStatus(str, enum.Enum):
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    shipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shipments.shipment_id"),
        unique=True,
        nullable=False,
        index=True,
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.company_id"),
        nullable=False,
        index=True,
    )
    truck_id = Column(
        UUID(as_uuid=True), ForeignKey("trucks.truck_id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True
    )
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shipment_matches.match_id"),
        unique=True,
        nullable=False,
    )

    status = Column(
        Enum(
            ReservationStatus,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="reservationstatus",
        ),
        nullable=False,
        default=ReservationStatus.ACCEPTED,
        server_default=ReservationStatus.ACCEPTED.value,
    )
    reserved_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shipment = relationship("Shipment", back_populates="reservation")
    company = relationship("Company", back_populates="reservations")
    truck = relationship("Truck", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
    match = relationship("ShipmentMatch", back_populates="reservation")
