from database import Base
import uuid
import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CompanyType(str, enum.Enum):
    SHIPPER = "shipper"
    FLEET = "fleet"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    RESUBMIT = "resubmit"
    REJECTED = "rejected"


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    company_type = Column(
        Enum(
            CompanyType,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="companytype",
        ),
        nullable=False,
    )
    business_name = Column(String(100), nullable=False)
    registration_number = Column(String(20), unique=True, nullable=False, index=True)
    company_email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(15), nullable=False)

    verification_status = Column(
        Enum(
            VerificationStatus,
            values_callable=lambda enum_class: [e.value for e in enum_class],
            name="verificationstatus",
        ),
        nullable=False,
        default=VerificationStatus.PENDING,
        server_default=VerificationStatus.PENDING.value,
        index=True,
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    certificate_file_url = Column(String(255), nullable=True)
    verification_failure_reason = Column(Text, nullable=True)
    fuel_price_per_litre = Column(Numeric(10, 2), nullable=True)
    driver_daily_allowance = Column(Numeric(10, 2), nullable=True)
    toll_assumption = Column(
        Numeric(10, 2), nullable=True, default=0, server_default="0"
    )
    other_costs = Column(Numeric(10, 2), nullable=True, default=0, server_default="0")
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
        CheckConstraint(
            "fuel_price_per_litre > 0", name="ck_companies_fuel_price_positive"
        ),
    )

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    trucks = relationship(
        "Truck", back_populates="company", cascade="all, delete-orphan"
    )
    shipments = relationship("Shipment", back_populates="company")
    reservations = relationship("Reservation", back_populates="company")
    audit_logs = relationship("AuditLog", back_populates="company")
