import pytest
import uuid
from sqlalchemy.exc import IntegrityError
import models


class TestAuditLog:
    def test_create_audit_log_happy_path(self, db_session, sample_user, sample_company):
        audit_log = models.AuditLog(
            user_id=sample_user.user_id,
            company_id=sample_company.company_id,
            action_type="create_shipment",
            entity_type="shipment",
            entity_id=uuid.uuid4(),
            details={"key": "value"},
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.audit_id is not None
        assert isinstance(audit_log.audit_id, uuid.UUID)
        assert audit_log.user_id == sample_user.user_id
        assert audit_log.company_id == sample_company.company_id
        assert audit_log.action_type == "create_shipment"
        assert audit_log.entity_type == "shipment"
        assert isinstance(audit_log.entity_id, uuid.UUID)
        assert audit_log.details == {"key": "value"}
        assert audit_log.created_at is not None

    def test_audit_log_optional_fields(self, db_session):
        audit_log = models.AuditLog(action_type="system_event")
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.user_id is None
        assert audit_log.company_id is None
        assert audit_log.entity_type is None
        assert audit_log.entity_id is None
        assert audit_log.details is None
        assert audit_log.created_at is not None

    def test_audit_log_with_user_only(self, db_session, sample_user):
        audit_log = models.AuditLog(
            user_id=sample_user.user_id,
            action_type="login",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.user_id == sample_user.user_id
        assert audit_log.company_id is None

    def test_audit_log_with_company_only(self, db_session, sample_company):
        audit_log = models.AuditLog(
            company_id=sample_company.company_id,
            action_type="update_company",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.company_id == sample_company.company_id
        assert audit_log.user_id is None

    def test_audit_log_missing_action_type(self, db_session):
        audit_log = models.AuditLog(details={"key": "value"})
        db_session.add(audit_log)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_audit_log_user_relationship(self, db_session, sample_user):
        audit_log = models.AuditLog(
            user_id=sample_user.user_id,
            action_type="create_shipment",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.user is not None
        assert audit_log.user.user_id == sample_user.user_id
        assert audit_log in sample_user.audit_logs

    def test_audit_log_company_relationship(self, db_session, sample_company):
        audit_log = models.AuditLog(
            company_id=sample_company.company_id,
            action_type="update_company",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.company is not None
        assert audit_log.company.company_id == sample_company.company_id
        assert audit_log in sample_company.audit_logs

    def test_audit_log_json_details(self, db_session):
        details = {"updated_fields": ["business_name"], "count": 1}
        audit_log = models.AuditLog(
            action_type="update_company",
            details=details,
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.details == details
