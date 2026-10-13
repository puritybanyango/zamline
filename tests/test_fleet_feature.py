from decimal import Decimal

import pytest
from fastapi import HTTPException

import models
from schemas.cost_settings import CostSettingsUpdate
from schemas.trucks import TruckCreate
from services.cost_settings import get_cost_settings, update_cost_settings
from services.trucks import create_truck, get_truck


def test_fleet_manager_creates_company_scoped_truck(
    db_session,
    sample_fleet_company,
    sample_fleet_user,
):
    sample_fleet_company.verification_status = models.VerificationStatus.VERIFIED
    db_session.commit()

    payload = TruckCreate(
        plate_number="ZM-5555",
        truck_type="Rigid",
        body_type=models.BodyType.BOX,
        capacity_kg=7500,
        fuel_consumption_l_per_100km=25,
        maintenance_per_km=Decimal("1.80"),
    )

    truck = create_truck(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        payload,
    )

    assert truck.company_id == sample_fleet_company.company_id
    assert truck.capacity_kg == 7500


def test_truck_cannot_be_read_through_another_company(
    db_session,
    sample_truck,
    sample_company,
):
    with pytest.raises(HTTPException) as error:
        get_truck(db_session, sample_company.company_id, sample_truck.truck_id)

    assert error.value.status_code == 404


def test_private_cost_settings_are_fleet_company_scoped(
    db_session,
    sample_fleet_company,
    sample_fleet_user,
    sample_company,
):
    payload = CostSettingsUpdate(
        fuel_price_per_litre=Decimal("1.75"),
        driver_daily_allowance=Decimal("120.00"),
        toll_assumption=Decimal("20.00"),
        other_costs=Decimal("15.00"),
    )

    company = update_cost_settings(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        payload,
    )

    assert company.fuel_price_per_litre == Decimal("1.75")

    with pytest.raises(HTTPException) as error:
        get_cost_settings(db_session, sample_company.company_id)

    assert error.value.status_code == 403
