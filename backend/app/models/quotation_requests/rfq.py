from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RFQStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class RFQ(Base):
    __tablename__ = "rfqs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rfq_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    purchase_request_id = Column(
        Integer,
        ForeignKey(
            "purchase_requests.id",
            ondelete="RESTRICT",
        ),
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

    status = Column(
        String(30),
        nullable=False,
        default=RFQStatus.DRAFT.value,
        index=True,
    )

    issue_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    submission_deadline = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
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

    purchase_request = relationship("PurchaseRequest",back_populates="rfqs")

    created_by_user = relationship("User")

    items = relationship(
        "RFQItem",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )

    vendors = relationship(
        "RFQVendor",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )