from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):

    id: int

    actor_type: str
    actor_id: str | None

    action: str

    resource_type: str
    resource_id: str

    previous_state: dict[str, Any] | None
    new_state: dict[str, Any] | None

    metadata: dict[str, Any] | None

    correlation_id: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AuditLogListResponse(BaseModel):

    total: int

    limit: int
    offset: int

    items: list[AuditLogResponse]