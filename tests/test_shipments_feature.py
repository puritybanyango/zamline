from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

import models
from schemas.shipments import ShipmentCreate
from services.shipments import cancel_shipment, create_shipment


def shipment_payload(cargo_type="grain"):
    return ShipmentCreate(
        origin_address="Lusaka",
        origin_latitude=-15.3875,
        origin_longitude=28.3228,
        destination_address="Ndola",
        destination_latitude=-12.9587,
        destination_longitude=28.6366,
        cargo_type=cargo_type,
        weight_kg=2500,
        required_body_type=models.BodyType.FLATBED,
        pickup_time=datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc),
        special_requirements=None,
        proposed_amount=Decimal("5000.00"),
    )


def test_shipper_creates_and_cancels_shipment(
    db_session,
    sample_company,
    sample_user,
):
    sample_company.verification_status = models.VerificationStatus.VERIFIED
    db_session.commit()

    shipment = create_shipment(
        db_session,
        sample_company.company_id,
        sample_user.user_id,
        shipment_payload(),
    )

    assert shipment.status == models.ShipmentStatus.OPEN
    assert shipment.weight_kg == 2500

    cancelled = cancel_shipment(
        db_session,
        sample_company.company_id,
        sample_user.user_id,
        shipment.shipment_id,
    )
    assert cancelled.status == models.ShipmentStatus.CANCELLED


def test_unaccepted_cargo_is_rejected_before_matching(
    db_session,
    sample_company,
    sample_user,
    monkeypatch,
):
    monkeypatch.setattr("services.shipments.UNACCEPTED_CARGO_TYPES", {"blocked-cargo"})

    with pytest.raises(HTTPException) as error:
        create_shipment(
            db_session,
            sample_company.company_id,
            sample_user.user_id,
            shipment_payload("blocked-cargo"),
        )

    assert error.value.status_code == 400
