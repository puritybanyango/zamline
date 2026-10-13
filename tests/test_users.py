import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
import models


class TestUser:
    def test_create_user_happy_path(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.user_id is not None
        assert isinstance(user.user_id, uuid.UUID)
        assert user.company_id == sample_company.company_id
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@test.com"
        assert user.password_hash == "hashed_password_123"
        assert user.role == models.UserRole.SHIPPER
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_user_with_fleet_manager_role(
        self, db_session, sample_fleet_company
    ):
        user = models.User(
            company_id=sample_fleet_company.company_id,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@fleet.com",
            password_hash="hashed_password_456",
            role=models.UserRole.FLEET_MANAGER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.role == models.UserRole.FLEET_MANAGER

    def test_user_default_is_active_true(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is True

    def test_user_explicit_is_active_false(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is False

    def test_user_unique_email_constraint(self, db_session, sample_company):
        user1 = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user1)
        db_session.commit()

        user2 = models.User(
            company_id=sample_company.company_id,
            first_name="Jane",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_456",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_missing_required_fields(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
        )
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_missing_password_hash(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user)
        db_session.commit()

        user2 = models.User(
            company_id=sample_company.company_id,
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@test.com",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_missing_role(self, db_session, sample_company):
        user = models.User(
            company_id=sample_company.company_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
        )
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_missing_company_id(self, db_session):
        user = models.User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password_hash="hashed_password_123",
            role=models.UserRole.SHIPPER,
        )
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_company_relationship(self, db_session, sample_user, sample_company):
        assert sample_user.company is not None
        assert sample_user.company.company_id == sample_company.company_id
        assert sample_user.company.business_name == sample_company.business_name

    def test_user_company_back_populates(self, db_session, sample_user, sample_company):
        assert sample_user in sample_company.users

    def test_user_shipments_relationship(self, db_session, sample_user, sample_company):
        shipment = models.Shipment(
            company_id=sample_company.company_id,
            user_id=sample_user.user_id,
            origin_address="123 Origin St",
            origin_latitude=40.7128,
            origin_longitude=-74.0060,
            destination_address="456 Dest Ave",
            destination_latitude=34.0522,
            destination_longitude=-118.2437,
            cargo_type="Electronics",
            weight_kg=5000.0,
            required_body_type=models.BodyType.FLATBED,
            pickup_time=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            proposed_amount=15000.00,
        )
        db_session.add(shipment)
        db_session.commit()
        db_session.refresh(shipment)

        assert shipment in sample_user.shipments
        assert len(sample_user.shipments) == 1

    def test_user_shipment_matches_relationship(
        self, db_session, sample_user, sample_shipment, sample_truck, sample_fleet_user
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            distance_km=500.0,
            duration=600,
            fuel_cost=1500.00,
            driver_cost=300.00,
            toll_cost=100.00,
            maintenance_cost=250.00,
            other_cost=50.00,
            estimated_total_cost=2200.00,
            proposed_amount=3000.00,
            estimated_margin=800.00,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match in sample_fleet_user.shipment_matches

    def test_user_reservations_relationship(
        self,
        db_session,
        sample_user,
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

        assert reservation in sample_fleet_user.reservations

    def test_user_audit_logs_relationship(self, db_session, sample_user):
        audit_log = models.AuditLog(
            user_id=sample_user.user_id,
            action_type="create_shipment",
            entity_type="shipment",
            entity_id=uuid.uuid4(),
            details={"key": "value"},
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log in sample_user.audit_logs
