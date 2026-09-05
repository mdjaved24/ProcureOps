from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"

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

    item_name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        String(500),
        nullable=True,
    )

    quantity = Column(
        Numeric(12, 2),
        nullable=False,
    )

    unit = Column(
        String(50),
        nullable=False,
        default="unit",
    )

    estimated_unit_price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    total_price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    purchase_request = relationship("PurchaseRequest",back_populates="items")