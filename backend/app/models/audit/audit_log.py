from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class AuditActorType(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Who performed the action?
    actor_type = Column(
        String(30),
        nullable=False,
    )

    actor_id = Column(
        String(100),
        nullable=True,
        index=True,
    )

    # What happened?
    action = Column(
        String(100),
        nullable=False,
        index=True,
    )

    # Which resource was affected?
    resource_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    # State before and after the action
    previous_state = Column(
        JSONB,
        nullable=True,
    )

    new_state = Column(
        JSONB,
        nullable=True,
    )

    # Additional structured information
    metadata_ = Column(
        "metadata",
        JSONB,
        nullable=True,
    )

    # Useful later for tracing one request/workflow
    correlation_id = Column(
        String(100),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )