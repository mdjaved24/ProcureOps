from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class PurchaseRequestStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    request_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    requester_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    estimated_amount = Column(
        Numeric(15, 2),
        nullable=False,
    )

    currency = Column(
        String(3),
        nullable=False,
        default="INR",
    )

    status = Column(
        String(30),
        nullable=False,
        default=PurchaseRequestStatus.DRAFT.value,
    )

    required_by_date = Column(
        DateTime,
        nullable=True,
    )

    policy_id = Column(
    Integer,
    ForeignKey(
        "policies.id",
        ondelete="RESTRICT",
    ),
    nullable=True,
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

    requester = relationship(
        "User",
    )

    department = relationship(
        "Department",
    )

    items = relationship(
        "PurchaseRequestItem",
        back_populates="purchase_request",
        cascade="all, delete-orphan",
    )

    policy = relationship("Policy")

    rfqs = relationship("RFQ",back_populates="purchase_request")