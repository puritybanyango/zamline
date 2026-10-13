from database import Base
import uuid
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ManagerDecision(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CLOSED = "closed"


class MatchOutcome(str, enum.Enum):
    PROFIT = "profit"
    LOSS = "loss"
    BREAK_EVEN = "break_even"


class ShipmentMatch(Base):
    __tablename__ = "shipment_matches"

    match_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    shipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shipments.shipment_id"),
        nullable=False,
        index=True,
    )
    truck_id = Column(
        UUID(as_uuid=True), ForeignKey("trucks.truck_id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True, index=True
    )
    distance_km = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    fuel_cost = Column(Numeric(12, 2), nullable=True)
    driver_cost = Column(Numeric(12, 2), nullable=True)
    toll_cost = Column(Numeric(12, 2), nullable=True)
    maintenance_cost = Column(Numeric(12, 2), nullable=True)
    other_cost = Column(Numeric(12, 2), nullable=True)
    estimated_total_cost = Column(Numeric(12, 2), nullable=True)
    proposed_amount = Column(Numeric(12, 2), nullable=True)
    estimated_margin = Column(Numeric(12, 2), nullable=True)
    outcome = Column(
        Enum(
            MatchOutcome,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="matchoutcome",
        ),
        nullable=True,
    )
    ai_explanation = Column(Text, nullable=True)

    manager_decision = Column(
        Enum(
            ManagerDecision,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="managerdecision",
        ),
        nullable=False,
        default=ManagerDecision.PENDING,
        server_default=ManagerDecision.PENDING.value,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "shipment_id", "truck_id", name="uq_shipment_matches_shipment_truck"
        ),
        Index("ix_shipment_matches_manager_decision", "manager_decision"),
    )

    shipment = relationship("Shipment", back_populates="matches")
    truck = relationship("Truck", back_populates="shipment_matches")
    user = relationship("User", back_populates="shipment_matches")
    reservation = relationship("Reservation", back_populates="match", uselist=False)
