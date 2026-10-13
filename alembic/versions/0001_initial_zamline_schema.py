"""Initial ZamLine schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_zamline_schema"
down_revision = None
branch_labels = None
depends_on = None

ENUMS = {
    "companytype": ("shipper", "fleet"),
    "verificationstatus": ("pending", "verified", "resubmit", "rejected"),
    "userrole": ("shipper", "fleet_manager"),
    "bodytype": ("flatbed", "box", "tanker", "refrigerated", "tipper", "container"),
    "availabilitystatus": ("available", "unavailable"),
    "shipmentstatus": ("open", "confirmed", "cancelled", "expired"),
    "matchoutcome": ("profit", "loss", "break_even"),
    "managerdecision": ("pending", "accepted", "declined", "closed"),
    "reservationstatus": ("accepted", "cancelled"),
}


def _enum(name):
    values = ENUMS[name]
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*values, name=name, create_type=False)
    return sa.Enum(*values, name=name)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for name, values in ENUMS.items():
            postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("company_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_type", _enum("companytype"), nullable=False),
        sa.Column("business_name", sa.String(100), nullable=False),
        sa.Column("registration_number", sa.String(20), nullable=False, unique=True),
        sa.Column("company_email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone_number", sa.String(15), nullable=False),
        sa.Column(
            "verification_status",
            _enum("verificationstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("certificate_file_url", sa.String(255), nullable=True),
        sa.Column("verification_failure_reason", sa.Text(), nullable=True),
        sa.Column("fuel_price_per_litre", sa.Numeric(10, 2), nullable=True),
        sa.Column("driver_daily_allowance", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "toll_assumption",
            sa.Numeric(10, 2),
            nullable=True,
            server_default="0",
        ),
        sa.Column("other_costs", sa.Numeric(10, 2), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "fuel_price_per_litre > 0",
            name="ck_companies_fuel_price_positive",
        ),
    )
    op.create_index("ix_companies_company_id", "companies", ["company_id"])
    op.create_index(
        "ix_companies_registration_number",
        "companies",
        ["registration_number"],
    )
    op.create_index("ix_companies_company_email", "companies", ["company_email"])
    op.create_index(
        "ix_companies_verification_status",
        "companies",
        ["verification_status"],
    )

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id"),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", _enum("userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"])
    op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "trucks",
        sa.Column("truck_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id"),
            nullable=False,
        ),
        sa.Column("plate_number", sa.String(20), nullable=False, unique=True),
        sa.Column("truck_type", sa.String(30), nullable=False),
        sa.Column("body_type", _enum("bodytype"), nullable=False),
        sa.Column("capacity_kg", sa.Float(), nullable=False),
        sa.Column("fuel_consumption_l_per_100km", sa.Float(), nullable=False),
        sa.Column("maintenance_per_km", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "availability_status",
            _enum("availabilitystatus"),
            nullable=False,
            server_default="available",
        ),
        sa.Column("current_location", sa.String(50), nullable=True),
        sa.Column("available_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("capacity_kg > 0", name="ck_trucks_capacity_positive"),
        sa.CheckConstraint(
            "fuel_consumption_l_per_100km > 0",
            name="ck_trucks_fuel_consumption_positive",
        ),
    )
    op.create_index("ix_trucks_truck_id", "trucks", ["truck_id"])
    op.create_index("ix_trucks_company_id", "trucks", ["company_id"])
    op.create_index("ix_trucks_plate_number", "trucks", ["plate_number"])
    op.create_index(
        "ix_trucks_availability_status",
        "trucks",
        ["availability_status"],
    )
    op.create_index("ix_trucks_body_type", "trucks", ["body_type"])

    op.create_table(
        "shipments",
        sa.Column("shipment_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            nullable=False,
        ),
        sa.Column("origin_address", sa.String(250), nullable=False),
        sa.Column("origin_latitude", sa.Numeric(9, 6, asdecimal=False), nullable=False),
        sa.Column(
            "origin_longitude",
            sa.Numeric(9, 6, asdecimal=False),
            nullable=False,
        ),
        sa.Column("destination_address", sa.String(250), nullable=False),
        sa.Column(
            "destination_latitude",
            sa.Numeric(9, 6, asdecimal=False),
            nullable=False,
        ),
        sa.Column(
            "destination_longitude",
            sa.Numeric(9, 6, asdecimal=False),
            nullable=False,
        ),
        sa.Column("cargo_type", sa.String(20), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("required_body_type", _enum("bodytype"), nullable=False),
        sa.Column("pickup_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("special_requirements", sa.Text(), nullable=True),
        sa.Column("proposed_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "status",
            _enum("shipmentstatus"),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "origin_latitude BETWEEN -90 AND 90",
            name="ck_shipments_origin_lat",
        ),
        sa.CheckConstraint(
            "origin_longitude BETWEEN -180 AND 180",
            name="ck_shipments_origin_lng",
        ),
        sa.CheckConstraint(
            "destination_latitude BETWEEN -90 AND 90",
            name="ck_shipments_dest_lat",
        ),
        sa.CheckConstraint(
            "destination_longitude BETWEEN -180 AND 180",
            name="ck_shipments_dest_lng",
        ),
        sa.CheckConstraint("weight_kg > 0", name="ck_shipments_weight_positive"),
        sa.CheckConstraint(
            "proposed_amount > 0",
            name="ck_shipments_amount_positive",
        ),
    )
    op.create_index("ix_shipments_shipment_id", "shipments", ["shipment_id"])
    op.create_index("ix_shipments_company_id", "shipments", ["company_id"])
    op.create_index("ix_shipments_user_id", "shipments", ["user_id"])
    op.create_index("ix_shipments_status", "shipments", ["status"])
    op.create_index(
        "ix_shipments_required_body_type",
        "shipments",
        ["required_body_type"],
    )

    op.create_table(
        "shipment_matches",
        sa.Column("match_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "shipment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shipments.shipment_id"),
            nullable=False,
        ),
        sa.Column(
            "truck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trucks.truck_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            nullable=True,
        ),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("fuel_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("driver_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("toll_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("maintenance_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("other_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimated_total_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("proposed_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimated_margin", sa.Numeric(12, 2), nullable=True),
        sa.Column("outcome", _enum("matchoutcome"), nullable=True),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column(
            "manager_decision",
            _enum("managerdecision"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "shipment_id",
            "truck_id",
            name="uq_shipment_matches_shipment_truck",
        ),
    )
    op.create_index(
        "ix_shipment_matches_match_id",
        "shipment_matches",
        ["match_id"],
    )
    op.create_index(
        "ix_shipment_matches_shipment_id",
        "shipment_matches",
        ["shipment_id"],
    )
    op.create_index(
        "ix_shipment_matches_truck_id",
        "shipment_matches",
        ["truck_id"],
    )
    op.create_index(
        "ix_shipment_matches_user_id",
        "shipment_matches",
        ["user_id"],
    )
    op.create_index(
        "ix_shipment_matches_manager_decision",
        "shipment_matches",
        ["manager_decision"],
    )

    op.create_table(
        "reservations",
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "shipment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shipments.shipment_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id"),
            nullable=False,
        ),
        sa.Column(
            "truck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("trucks.truck_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            nullable=False,
        ),
        sa.Column(
            "match_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shipment_matches.match_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "status",
            _enum("reservationstatus"),
            nullable=False,
            server_default="accepted",
        ),
        sa.Column(
            "reserved_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_reservations_reservation_id",
        "reservations",
        ["reservation_id"],
    )
    op.create_index("ix_reservations_shipment_id", "reservations", ["shipment_id"])
    op.create_index("ix_reservations_company_id", "reservations", ["company_id"])
    op.create_index("ix_reservations_truck_id", "reservations", ["truck_id"])
    op.create_index("ix_reservations_user_id", "reservations", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "details",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_audit_logs_audit_id", "audit_logs", ["audit_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_company_id", "audit_logs", ["company_id"])
    op.create_index("ix_audit_logs_action_type", "audit_logs", ["action_type"])
    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        ["entity_type", "entity_id"],
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reservations")
    op.drop_table("shipment_matches")
    op.drop_table("shipments")
    op.drop_table("trucks")
    op.drop_table("users")
    op.drop_table("companies")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for name, values in reversed(list(ENUMS.items())):
            postgresql.ENUM(*values, name=name).drop(bind, checkfirst=True)
