from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit.audit_log import (
    AuditActorType,
    AuditLog,
)

class AuditService:

    @staticmethod
    def log(
        db: Session,
        *,
        actor_type: AuditActorType | str,
        actor_id: int | str | None,
        action: str,
        resource_type: str,
        resource_id: int | str,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> AuditLog:
        """
        Creates an audit log entry.

        The transaction is controlled by the caller.
        This method uses flush() instead of commit() so that
        the audit event participates in the same database transaction
        as the business operation.
        """

        audit_log = AuditLog(
            actor_type = (
                actor_type.value 
                if isinstance(actor_type, AuditActorType)
                else actor_type
            ),
            actor_id = (
                str(actor_id)
                if actor_id is not None
                else None
            ),
            action = action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            previous_state=previous_state,
            new_state=new_state,
            metadata_=metadata,
            correlation_id=correlation_id,
        )

        db.add(audit_log)

        db.flush()

        return audit_log



    @staticmethod
    def list_logs(
        db: Session,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:

        query = db.query(AuditLog)

        # ==========================================
        # Filters
        # ==========================================

        if resource_type is not None:
            query = query.filter(AuditLog.resource_type == resource_type)

        if resource_id is not None:
            query = query.filter(AuditLog.resource_id == str(resource_id))

        if actor_id is not None:
            query = query.filter(AuditLog.actor_id == str(actor_id))

        if action is not None:
            query = query.filter(AuditLog.action == action)

        if start_date is not None:
            query = query.filter(AuditLog.created_at >= start_date)

        if end_date is not None:
            query = query.filter(AuditLog.created_at <= end_date)

        # ==========================================
        # Count before pagination
        # ==========================================

        total = query.count()

        # ==========================================
        # Pagination
        # ==========================================

        logs = query.order_by(
                AuditLog.created_at.desc(),
                AuditLog.id.desc(),
            ).limit(limit).offset(offset).all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": log.id,

                    "actor_type": log.actor_type,
                    "actor_id": log.actor_id,

                    "action": log.action,

                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,

                    "previous_state": log.previous_state,
                    "new_state": log.new_state,

                    "metadata": log.metadata_,

                    "correlation_id": log.correlation_id,

                    "created_at": log.created_at,
                }
                for log in logs
            ],
        }