from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RFQItem(Base):
    __tablename__ = "rfq_items"

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

    # Original purchase request item
    purchase_request_item_id = Column(
        Integer,
        ForeignKey(
            "purchase_request_items.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    item_name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    quantity = Column(
        Numeric(12, 2),
        nullable=False,
    )

    unit = Column(
        String(50),
        nullable=False,
    )

    rfq = relationship("RFQ",back_populates="items")

    purchase_request_item = relationship("PurchaseRequestItem")