from models.users import UserRole
from schemas.users import RegisterRequest
from services.users import login_user, register_user, verify_user_otp


def test_registration_otp_and_login_flow(db_session, monkeypatch):
    sent = {}

    def fake_send(email, code):
        sent["email"] = email
        sent["code"] = code

    monkeypatch.setattr("services.users.send_otp_email", fake_send)
    monkeypatch.setattr(
        "services.users.hash_password",
        lambda password: f"hashed::{password}",
    )
    monkeypatch.setattr(
        "services.users.verify_password",
        lambda password, stored: stored == f"hashed::{password}",
    )
    monkeypatch.setattr(
        "security.tokens.JWT_SECRET",
        "test-secret-key-long-enough-for-hs256-123456",
    )

    request = RegisterRequest(
        company_type="shipper",
        business_name="New Shipper",
        registration_number="NEW-001",
        company_email="office@newshipper.com",
        phone_number="+260970000001",
        first_name="Amina",
        last_name="Banda",
        email="amina@newshipper.com",
        password="StrongPass123!",
        role=UserRole.SHIPPER,
    )

    user = register_user(db_session, request)

    assert user.is_active is False
    assert user.password_hash != request.password
    assert sent["email"] == "amina@newshipper.com"

    verified = verify_user_otp(db_session, user.email, sent["code"])
    assert verified.is_active is True

    token = login_user(db_session, user.email, request.password)
    assert isinstance(token, str)
    assert token


def test_registration_rejects_role_company_mismatch(db_session, monkeypatch):
    from fastapi import HTTPException
    import pytest

    monkeypatch.setattr("services.users.send_otp_email", lambda email, code: None)

    request = RegisterRequest(
        company_type="shipper",
        business_name="Wrong Role Ltd",
        registration_number="WRONG-001",
        company_email="office@wrongrole.com",
        phone_number="+260970000002",
        first_name="Wrong",
        last_name="Role",
        email="wrong@wrongrole.com",
        password="StrongPass123!",
        role=UserRole.FLEET_MANAGER,
    )

    with pytest.raises(HTTPException) as error:
        register_user(db_session, request)

    assert error.value.status_code == 400
