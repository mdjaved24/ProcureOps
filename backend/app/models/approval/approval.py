from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    CANCELLED = "CANCELLED"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    purchase_request_id = Column(
        Integer,
        ForeignKey(
            "purchase_requests.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default=ApprovalStatus.PENDING.value,
    )

    approval_type = Column(
        String(30),
        nullable=False,
        default="ALL_REQUIRED",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    purchase_request = relationship(
        "PurchaseRequest",
    )

    steps = relationship(
        "ApprovalStep",
        back_populates="approval",
        cascade="all, delete-orphan",
    )