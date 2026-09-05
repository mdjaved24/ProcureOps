from enum import Enum
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class VendorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    vendor_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    email = Column(
        String(255),
        nullable=False,
        index=True,
    )

    phone = Column(
        String(50),
        nullable=False,
    )

    address = Column(
        Text,
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    state = Column(
        String(100),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    postal_code = Column(
        String(20),
        nullable=True,
    )

    tax_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default=VendorStatus.ACTIVE.value,
        index=True,
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

    # Relationship with RFQVendor (for RFQ invitations)
    rfq_invitations = relationship(
        "RFQVendor",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )

    # Relationship with VendorUser (for vendor users)
    vendor_users = relationship(
        "VendorUser",
        back_populates="vendor",
        cascade="all, delete-orphan",
        lazy="select",
    )