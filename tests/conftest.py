import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
import models


SAMPLE_PICKUP_TIME = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.rollback()
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def sample_company(db_session):
    company = models.Company(
        company_type=models.CompanyType.SHIPPER,
        business_name="Test Company",
        registration_number="REG123456",
        company_email="test@company.com",
        phone_number="+1234567890",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_fleet_company(db_session):
    company = models.Company(
        company_type=models.CompanyType.FLEET,
        business_name="Test Fleet Co",
        registration_number="REG789012",
        company_email="fleet@company.com",
        phone_number="+0987654321",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_user(db_session, sample_company):
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
    return user


@pytest.fixture
def sample_fleet_user(db_session, sample_fleet_company):
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
    return user


@pytest.fixture
def sample_truck(db_session, sample_fleet_company):
    truck = models.Truck(
        company_id=sample_fleet_company.company_id,
        plate_number="ABC-1234",
        truck_type="Heavy Duty",
        body_type=models.BodyType.FLATBED,
        capacity_kg=10000.0,
        fuel_consumption_l_per_100km=30.0,
        maintenance_per_km=2.50,
    )
    db_session.add(truck)
    db_session.commit()
    db_session.refresh(truck)
    return truck


@pytest.fixture
def sample_shipment(db_session, sample_company, sample_user):
    shipment = models.Shipment(
        company_id=sample_company.company_id,
        user_id=sample_user.user_id,
        origin_address="123 Origin St, City A",
        origin_latitude=40.7128,
        origin_longitude=-74.0060,
        destination_address="456 Dest Ave, City B",
        destination_latitude=34.0522,
        destination_longitude=-118.2437,
        cargo_type="Electronics",
        weight_kg=5000.0,
        required_body_type=models.BodyType.FLATBED,
        pickup_time=SAMPLE_PICKUP_TIME,
        proposed_amount=15000.00,
    )
    db_session.add(shipment)
    db_session.commit()
    db_session.refresh(shipment)
    return shipment


@pytest.fixture
def sample_match(db_session, sample_shipment, sample_truck, sample_fleet_user):
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
        ai_explanation="Good match based on location and capacity",
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


@pytest.fixture
def sample_reservation(
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
    return reservation
