from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_admin
from models import AuditLog, User
from schemas import AdminAuditLogResponse


router = APIRouter(
    prefix="/admin/audit-logs",
    tags=["Admin - Audit Logs"]
)


@router.get("/", response_model=list[AdminAuditLogResponse])
def get_audit_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Retrieve audit logs, newest events first.
    logs = (
        db.query(AuditLog)
        .order_by(
            AuditLog.timestamp.desc(),
            AuditLog.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return logs
