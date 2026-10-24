
from fastapi import Request
from sqlalchemy.orm import Session

from models import AuditLog


def write_audit_log(
    db: Session,
    request: Request,
    event_type: str,
    result: str,
    username: str = None,
    reason: str = None
):
    """Save a security event without recording secrets."""

    log_entry = AuditLog(
        username=username,
        ip_address=(
            request.client.host
            if request.client is not None
            else None
        ),
        event_type=event_type,
        result=result,
        reason=reason
    )

    db.add(log_entry)

    # Persist the audit event immediately.
    db.commit()
