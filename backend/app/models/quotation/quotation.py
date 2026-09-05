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


class QuotationStatus(str, Enum):

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class Quotation(Base):

    __tablename__ = "quotations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rfq_vendor_id = Column(
        Integer,
        ForeignKey(
            "rfq_vendors.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    quotation_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default=QuotationStatus.DRAFT.value,
        index=True,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="INR",
    )

    subtotal = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
    )

    tax_amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
    )

    total_amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
    )

    valid_until = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    submitted_at = Column(
        DateTime(timezone=True),
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

    rfq_vendor = relationship("RFQVendor",back_populates="quotation")

    items = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )