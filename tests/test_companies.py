import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
import models


class TestCompany:
    def test_create_shipper_company_happy_path(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Shipper Co",
            registration_number="REG123456",
            company_email="shipper@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.company_id is not None
        assert isinstance(company.company_id, uuid.UUID)
        assert company.company_type == models.CompanyType.SHIPPER
        assert company.business_name == "Test Shipper Co"
        assert company.registration_number == "REG123456"
        assert company.company_email == "shipper@test.com"
        assert company.phone_number == "+1234567890"
        assert company.verification_status == models.VerificationStatus.PENDING
        assert company.verified_at is None
        assert company.certificate_file_url is None
        assert company.verification_failure_reason is None
        assert company.fuel_price_per_litre is None
        assert company.driver_daily_allowance is None
        assert company.toll_assumption == Decimal("0")
        assert company.other_costs == Decimal("0")
        assert company.created_at is not None
        assert company.updated_at is not None

    def test_create_fleet_company_happy_path(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet Co",
            registration_number="REG789012",
            company_email="fleet@test.com",
            phone_number="+0987654321",
            fuel_price_per_litre=Decimal("1.50"),
            driver_daily_allowance=Decimal("100.00"),
            toll_assumption=Decimal("50.00"),
            other_costs=Decimal("25.00"),
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.company_type == models.CompanyType.FLEET
        assert company.fuel_price_per_litre == Decimal("1.50")
        assert company.driver_daily_allowance == Decimal("100.00")
        assert company.toll_assumption == Decimal("50.00")
        assert company.other_costs == Decimal("25.00")

    def test_company_default_verification_status_pending(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            registration_number="REG123456",
            company_email="test@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.verification_status == models.VerificationStatus.PENDING

    def test_company_explicit_verification_status(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            registration_number="REG123456",
            company_email="test@test.com",
            phone_number="+1234567890",
            verification_status=models.VerificationStatus.VERIFIED,
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.verification_status == models.VerificationStatus.VERIFIED

    def test_company_default_toll_assumption_zero(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet",
            registration_number="REG123456",
            company_email="fleet@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.toll_assumption == Decimal("0")

    def test_company_default_other_costs_zero(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet",
            registration_number="REG123456",
            company_email="fleet@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.other_costs == Decimal("0")

    def test_company_unique_registration_number(self, db_session):
        company1 = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Company One",
            registration_number="REG123456",
            company_email="one@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company1)
        db_session.commit()

        company2 = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Company Two",
            registration_number="REG123456",
            company_email="two@test.com",
            phone_number="+0987654321",
        )
        db_session.add(company2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_unique_email(self, db_session):
        company1 = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Company One",
            registration_number="REG123456",
            company_email="test@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company1)
        db_session.commit()

        company2 = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Company Two",
            registration_number="REG789012",
            company_email="test@test.com",
            phone_number="+0987654321",
        )
        db_session.add(company2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_required_fields(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            registration_number="REG123456",
            company_email="test@test.com",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_company_type(self, db_session):
        company = models.Company(
            business_name="Test Co",
            registration_number="REG123456",
            company_email="test@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_business_name(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            registration_number="REG123456",
            company_email="test@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_registration_number(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            company_email="test@test.com",
            phone_number="+1234567890",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_company_email(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            registration_number="REG123456",
            phone_number="+1234567890",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_missing_phone_number(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.SHIPPER,
            business_name="Test Co",
            registration_number="REG123456",
            company_email="test@test.com",
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_fuel_price_positive_constraint(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet",
            registration_number="REG123456",
            company_email="fleet@test.com",
            phone_number="+1234567890",
            fuel_price_per_litre=Decimal("-1.00"),
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_fuel_price_zero_constraint(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet",
            registration_number="REG123456",
            company_email="fleet@test.com",
            phone_number="+1234567890",
            fuel_price_per_litre=Decimal("0"),
        )
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_valid_fuel_price(self, db_session):
        company = models.Company(
            company_type=models.CompanyType.FLEET,
            business_name="Test Fleet",
            registration_number="REG123456",
            company_email="fleet@test.com",
            phone_number="+1234567890",
            fuel_price_per_litre=Decimal("1.50"),
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.fuel_price_per_litre == Decimal("1.50")

    def test_company_users_relationship(self, db_session, sample_company, sample_user):
        assert sample_user in sample_company.users
        assert len(sample_company.users) == 1

    def test_company_trucks_relationship(
        self, db_session, sample_fleet_company, sample_truck
    ):
        assert sample_truck in sample_fleet_company.trucks
        assert len(sample_fleet_company.trucks) == 1

    def test_company_shipments_relationship(
        self, db_session, sample_company, sample_user
    ):
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

        assert shipment in sample_company.shipments
        assert len(sample_company.shipments) == 1

    def test_company_reservations_relationship(
        self,
        db_session,
        sample_fleet_company,
        sample_shipment,
        sample_match,
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

        assert reservation in sample_fleet_company.reservations
        assert len(sample_fleet_company.reservations) == 1

    def test_company_audit_logs_relationship(self, db_session, sample_company):
        audit_log = models.AuditLog(
            company_id=sample_company.company_id,
            action_type="update_company",
            entity_type="company",
            entity_id=sample_company.company_id,
            details={"updated_fields": ["business_name"]},
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log in sample_company.audit_logs
        assert len(sample_company.audit_logs) == 1

    def test_company_cascade_delete_users(
        self, db_session, sample_company, sample_user
    ):
        user_id = sample_user.user_id
        db_session.delete(sample_company)
        db_session.commit()

        deleted_user = (
            db_session.query(models.User).filter(models.User.user_id == user_id).first()
        )
        assert deleted_user is None

    def test_company_cascade_delete_trucks(
        self, db_session, sample_fleet_company, sample_truck
    ):
        truck_id = sample_truck.truck_id
        db_session.delete(sample_fleet_company)
        db_session.commit()

        deleted_truck = (
            db_session.query(models.Truck)
            .filter(models.Truck.truck_id == truck_id)
            .first()
        )
        assert deleted_truck is None
