import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
import models


class TestReservation:
    def test_create_reservation_happy_path(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.reservation_id is not None
        assert isinstance(reservation.reservation_id, uuid.UUID)
        assert reservation.shipment_id == sample_shipment.shipment_id
        assert reservation.company_id == sample_fleet_company.company_id
        assert reservation.truck_id == sample_truck.truck_id
        assert reservation.user_id == sample_fleet_user.user_id
        assert reservation.match_id == sample_match.match_id
        assert reservation.status == models.ReservationStatus.ACCEPTED
        assert reservation.reserved_at is not None

    def test_reservation_default_status_accepted(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.status == models.ReservationStatus.ACCEPTED

    def test_reservation_explicit_status_cancelled(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
            status=models.ReservationStatus.CANCELLED,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.status == models.ReservationStatus.CANCELLED

    def test_reservation_missing_required_fields(self, db_session):
        reservation = models.Reservation()
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_missing_shipment_id(
        self,
        db_session,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_missing_company_id(
        self, db_session, sample_shipment, sample_match, sample_truck, sample_fleet_user
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_missing_truck_id(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_missing_user_id(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_missing_match_id(
        self,
        db_session,
        sample_shipment,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
        )
        db_session.add(reservation)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_unique_shipment_id(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
        sample_company,
        sample_user,
    ):
        reservation1 = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation1)
        db_session.commit()

        other_shipment = models.Shipment(
            company_id=sample_company.company_id,
            user_id=sample_user.user_id,
            origin_address="Lusaka",
            origin_latitude=-15.3875,
            origin_longitude=28.3228,
            destination_address="Ndola",
            destination_latitude=-12.9587,
            destination_longitude=28.6366,
            cargo_type="Grain",
            weight_kg=1000.0,
            required_body_type=models.BodyType.FLATBED,
            pickup_time=datetime(2026, 11, 15, 10, 0, 0, tzinfo=timezone.utc),
            proposed_amount=3000.00,
        )
        db_session.add(other_shipment)
        db_session.commit()
        db_session.refresh(other_shipment)

        other_match = models.ShipmentMatch(
            shipment_id=other_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
        )
        db_session.add(other_match)
        db_session.commit()
        db_session.refresh(other_match)

        reservation2 = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=other_match.match_id,
        )
        db_session.add(reservation2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_unique_match_id(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
        sample_company,
        sample_user,
    ):
        reservation1 = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation1)
        db_session.commit()

        other_shipment = models.Shipment(
            company_id=sample_company.company_id,
            user_id=sample_user.user_id,
            origin_address="Lusaka",
            origin_latitude=-15.3875,
            origin_longitude=28.3228,
            destination_address="Ndola",
            destination_latitude=-12.9587,
            destination_longitude=28.6366,
            cargo_type="Grain",
            weight_kg=1000.0,
            required_body_type=models.BodyType.FLATBED,
            pickup_time=datetime(2026, 11, 15, 10, 0, 0, tzinfo=timezone.utc),
            proposed_amount=3000.00,
        )
        db_session.add(other_shipment)
        db_session.commit()
        db_session.refresh(other_shipment)

        other_match = models.ShipmentMatch(
            shipment_id=other_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
        )
        db_session.add(other_match)
        db_session.commit()
        db_session.refresh(other_match)

        reservation2 = models.Reservation(
            shipment_id=other_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_reservation_shipment_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert sample_shipment.reservation is not None
        assert sample_shipment.reservation.reservation_id == reservation.reservation_id

    def test_reservation_company_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.company.company_id == sample_fleet_company.company_id
        assert reservation in sample_fleet_company.reservations

    def test_reservation_truck_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.truck.truck_id == sample_truck.truck_id
        assert reservation in sample_truck.reservations

    def test_reservation_user_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.user.user_id == sample_fleet_user.user_id
        assert reservation in sample_fleet_user.reservations

    def test_reservation_match_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert reservation.match.match_id == sample_match.match_id
        assert sample_match.reservation.reservation_id == reservation.reservation_id
