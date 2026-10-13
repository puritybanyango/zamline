# Owner: Shared Team
# Feature: Cross-cutting audit logging

from sqlalchemy.orm import Session

from models.audit_logs import AuditLog


def create_audit_log(db: Session, **values):
    audit_log = AuditLog(**values)
    db.add(audit_log)
    db.flush()
    return audit_log
