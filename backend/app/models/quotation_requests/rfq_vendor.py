from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RFQVendorStatus(str, Enum):
    INVITED = "INVITED"
    RESPONDED = "RESPONDED"
    DECLINED = "DECLINED"


class RFQVendor(Base):
    __tablename__ = "rfq_vendors"

    __table_args__ = (
        UniqueConstraint(
            "rfq_id",
            "vendor_id",
            name="uq_rfq_vendor",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rfq_id = Column(
        Integer,
        ForeignKey(
            "rfqs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    vendor_id = Column(
        Integer,
        ForeignKey(
            "vendors.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default=RFQVendorStatus.INVITED.value,
    )

    invited_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    rfq = relationship("RFQ",back_populates="vendors")

    vendor = relationship("Vendor",back_populates="rfq_invitations")

    quotation = relationship(
    "Quotation",
    back_populates="rfq_vendor",
    uselist=False,
    cascade="all, delete-orphan",
    )