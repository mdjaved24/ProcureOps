from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class VendorUser(Base):
    __tablename__ = "vendor_users"

    id = Column(Integer, primary_key=True, index=True)
    
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Link to internal user (for admin-managed users)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
    )
    
    full_name = Column(
        String(150),
        nullable=False,
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
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

    vendor = relationship("Vendor",back_populates="vendor_users")
    
    user = relationship("User",back_populates="vendor_user")