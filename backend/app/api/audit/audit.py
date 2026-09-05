from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.authorization import require_permission

from app.schemas.audit.audit_log import (
    AuditLogListResponse,
)
from app.services.audit.audit_service import AuditService


audit_router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@audit_router.get(
    "",
    response_model=AuditLogListResponse,
)
def list_audit_logs(

    resource_type: str | None = Query(
        default=None,
    ),

    resource_id: str | None = Query(
        default=None,
    ),

    actor_id: str | None = Query(
        default=None,
    ),

    action: str | None = Query(
        default=None,
    ),

    start_date: datetime | None = Query(
        default=None,
    ),

    end_date: datetime | None = Query(
        default=None,
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(get_db),

    current_user = Depends(
        require_permission("AUDIT_LOG_READ")
    ),

):
    return AuditService.list_logs(
        db=db,

        resource_type=resource_type,
        resource_id=resource_id,

        actor_id=actor_id,

        action=action,

        start_date=start_date,
        end_date=end_date,

        limit=limit,
        offset=offset,
    )