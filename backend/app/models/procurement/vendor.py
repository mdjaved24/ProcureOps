from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.core.database import Base


class VendorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    BLACKLISTED = "BLACKLISTED"


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

    legal_name = Column(
        String(255),
        nullable=False,
    )

    display_name = Column(
        String(255),
        nullable=True,
    )

    email = Column(
        String(255),
        nullable=True,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    tax_identifier = Column(
        String(100),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default=VendorStatus.ACTIVE.value,
    )

    description = Column(
        Text,
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