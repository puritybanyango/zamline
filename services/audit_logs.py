# Owner: Shared Team
# Feature: Cross-cutting audit logging

from uuid import UUID

from sqlalchemy.orm import Session

from repositories.audit_logs import create_audit_log


def record_event(
    db: Session,
    action_type: str,
    user_id: UUID | None = None,
    company_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    details: dict | None = None,
):
    return create_audit_log(
        db,
        user_id=user_id,
        company_id=company_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
