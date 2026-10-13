import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
import models


class TestTruck:
    def test_create_truck_happy_path(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        db_session.commit()
        db_session.refresh(truck)

        assert truck.truck_id is not None
        assert isinstance(truck.truck_id, uuid.UUID)
        assert truck.company_id == sample_fleet_company.company_id
        assert truck.plate_number == "ABC-1234"
        assert truck.truck_type == "Heavy Duty"
        assert truck.body_type == models.BodyType.FLATBED
        assert truck.capacity_kg == 10000.0
        assert truck.fuel_consumption_l_per_100km == 30.0
        assert truck.maintenance_per_km == Decimal("2.50")
        assert truck.availability_status == models.AvailabilityStatus.AVAILABLE
        assert truck.current_location is None
        assert truck.available_from is None
        assert truck.created_at is not None
        assert truck.updated_at is not None

    def test_create_truck_all_body_types(self, db_session, sample_fleet_company):
        for body_type in models.BodyType:
            truck = models.Truck(
                company_id=sample_fleet_company.company_id,
                plate_number=f"TEST-{body_type.value.upper()[:4]}",
                truck_type="Test Truck",
                body_type=body_type,
                capacity_kg=10000.0,
                fuel_consumption_l_per_100km=30.0,
                maintenance_per_km=Decimal("2.50"),
            )
            db_session.add(truck)
            db_session.commit()
            db_session.refresh(truck)

            assert truck.body_type == body_type

    def test_truck_default_availability_status_available(
        self, db_session, sample_fleet_company
    ):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        db_session.commit()
        db_session.refresh(truck)

        assert truck.availability_status == models.AvailabilityStatus.AVAILABLE

    def test_truck_explicit_availability_status_unavailable(
        self, db_session, sample_fleet_company
    ):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
            availability_status=models.AvailabilityStatus.UNAVAILABLE,
        )
        db_session.add(truck)
        db_session.commit()
        db_session.refresh(truck)

        assert truck.availability_status == models.AvailabilityStatus.UNAVAILABLE

    def test_truck_unique_plate_number(self, db_session, sample_fleet_company):
        truck1 = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck1)
        db_session.commit()

        truck2 = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Light Duty",
            body_type=models.BodyType.BOX,
            capacity_kg=5000.0,
            fuel_consumption_l_per_100km=20.0,
            maintenance_per_km=Decimal("1.50"),
        )
        db_session.add(truck2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_missing_required_fields(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_missing_company_id(self, db_session):
        truck = models.Truck(
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_missing_plate_number(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_missing_body_type(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_capacity_positive_constraint(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=-1000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_capacity_zero_constraint(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_fuel_consumption_positive_constraint(
        self, db_session, sample_fleet_company
    ):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=-5.0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_fuel_consumption_zero_constraint(
        self, db_session, sample_fleet_company
    ):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=0,
            maintenance_per_km=Decimal("2.50"),
        )
        db_session.add(truck)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_truck_optional_fields(self, db_session, sample_fleet_company):
        truck = models.Truck(
            company_id=sample_fleet_company.company_id,
            plate_number="ABC-1234",
            truck_type="Heavy Duty",
            body_type=models.BodyType.FLATBED,
            capacity_kg=10000.0,
            fuel_consumption_l_per_100km=30.0,
            maintenance_per_km=Decimal("2.50"),
            current_location="Warehouse A",
            available_from=datetime(2026, 1, 15, 8, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(truck)
        db_session.commit()
        db_session.refresh(truck)

        assert truck.current_location == "Warehouse A"
        assert truck.available_from is not None

    def test_truck_company_relationship(
        self, db_session, sample_truck, sample_fleet_company
    ):
        assert sample_truck.company is not None
        assert sample_truck.company.company_id == sample_fleet_company.company_id
        assert sample_truck.company.business_name == sample_fleet_company.business_name

    def test_truck_company_back_populates(
        self, db_session, sample_truck, sample_fleet_company
    ):
        assert sample_truck in sample_fleet_company.trucks

    def test_truck_shipment_matches_relationship(
        self, db_session, sample_truck, sample_shipment, sample_fleet_user
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

        assert match in sample_truck.shipment_matches
        assert len(sample_truck.shipment_matches) == 1

    def test_truck_reservations_relationship(
        self,
        db_session,
        sample_truck,
        sample_shipment,
        sample_match,
        sample_fleet_company,
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

        assert reservation in sample_truck.reservations
        assert len(sample_truck.reservations) == 1

    def test_truck_cascade_delete_on_company_delete(
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
