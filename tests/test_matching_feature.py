import pytest
from fastapi import HTTPException

import models
from repositories.reservations import get_reservation_by_shipment
from repositories.shipment_matches import list_company_matches
from services.reservations import get_contact_handoff
from services.shipment_matches import decide_match, refresh_matches


def test_refresh_matching_uses_weight_body_type_and_availability(
    db_session,
    sample_company,
    sample_fleet_company,
    sample_user,
    sample_fleet_user,
    sample_shipment,
    sample_truck,
):
    sample_company.verification_status = models.VerificationStatus.VERIFIED
    sample_fleet_company.verification_status = models.VerificationStatus.VERIFIED
    db_session.commit()

    created = refresh_matches(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
    )

    matches = list_company_matches(db_session, sample_fleet_company.company_id)
    assert created == 1
    assert len(matches) == 1
    assert matches[0].shipment_id == sample_shipment.shipment_id
    assert matches[0].truck_id == sample_truck.truck_id


def test_first_acceptance_creates_reservation_and_closes_shipment(
    db_session,
    sample_company,
    sample_fleet_company,
    sample_fleet_user,
    sample_shipment,
    sample_truck,
):
    sample_company.verification_status = models.VerificationStatus.VERIFIED
    sample_fleet_company.verification_status = models.VerificationStatus.VERIFIED
    db_session.commit()

    refresh_matches(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
    )
    match = list_company_matches(db_session, sample_fleet_company.company_id)[0]

    accepted = decide_match(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        match.match_id,
        models.ManagerDecision.ACCEPTED,
    )

    reservation = get_reservation_by_shipment(db_session, sample_shipment.shipment_id)

    assert accepted.manager_decision == models.ManagerDecision.ACCEPTED
    assert reservation is not None
    assert sample_shipment.status == models.ShipmentStatus.CONFIRMED
    assert sample_truck.availability_status == models.AvailabilityStatus.UNAVAILABLE


def test_contact_handoff_only_for_reservation_parties(
    db_session,
    sample_company,
    sample_fleet_company,
    sample_user,
    sample_fleet_user,
    sample_shipment,
    sample_truck,
):
    sample_company.verification_status = models.VerificationStatus.VERIFIED
    sample_fleet_company.verification_status = models.VerificationStatus.VERIFIED
    db_session.commit()

    refresh_matches(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
    )
    match = list_company_matches(db_session, sample_fleet_company.company_id)[0]
    decide_match(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        match.match_id,
        models.ManagerDecision.ACCEPTED,
    )
    reservation = get_reservation_by_shipment(db_session, sample_shipment.shipment_id)

    fleet_contact = get_contact_handoff(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        reservation.reservation_id,
    )
    shipper_contact = get_contact_handoff(
        db_session,
        sample_company.company_id,
        sample_user.user_id,
        reservation.reservation_id,
    )

    assert fleet_contact["business_name"] == sample_company.business_name
    assert shipper_contact["business_name"] == sample_fleet_company.business_name


def test_other_company_cannot_view_reservation(
    db_session,
    sample_company,
    sample_fleet_company,
    sample_user,
    sample_fleet_user,
    sample_shipment,
    sample_truck,
):
    from models.companies import Company, CompanyType
    from services.reservations import get_reservation

    sample_company.verification_status = models.VerificationStatus.VERIFIED
    sample_fleet_company.verification_status = models.VerificationStatus.VERIFIED

    outsider = Company(
        company_type=CompanyType.FLEET,
        business_name="Outsider Fleet",
        registration_number="OUT-001",
        company_email="outsider@example.com",
        phone_number="+260970999999",
    )
    db_session.add(outsider)
    db_session.commit()
    db_session.refresh(outsider)

    refresh_matches(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
    )
    match = list_company_matches(db_session, sample_fleet_company.company_id)[0]
    decide_match(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        match.match_id,
        models.ManagerDecision.ACCEPTED,
    )
    reservation = get_reservation_by_shipment(db_session, sample_shipment.shipment_id)

    with pytest.raises(HTTPException) as error:
        get_reservation(db_session, outsider.company_id, reservation.reservation_id)

    assert error.value.status_code == 404
