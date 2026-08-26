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


class ApprovalStepStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"


class ApprovalStep(Base):
    __tablename__ = "approval_steps"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    approval_id = Column(
        Integer,
        ForeignKey(
            "approvals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    required_role = Column(
        String(100),
        nullable=False,
    )

    sequence = Column(
        Integer,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default=ApprovalStepStatus.PENDING.value,
    )

    decided_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    decision_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    decision_comments = Column(
    String(2000),
    nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    approval = relationship(
        "Approval",
        back_populates="steps",
    )

    approver = relationship(
        "User",
    )