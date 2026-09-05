from decimal import Decimal

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class QuotationItem(Base):

    __tablename__ = "quotation_items"

    __table_args__ = (
    UniqueConstraint(
    "quotation_id",
    "rfq_item_id",
    name="uq_quotation_item_rfq_item",
    ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    quotation_id = Column(
        Integer,
        ForeignKey(
            "quotations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rfq_item_id = Column(
        Integer,
        ForeignKey(
            "rfq_items.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
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
        Numeric(18, 2),
        nullable=False,
    )

    unit = Column(
        String(50),
        nullable=False,
    )

    unit_price = Column(
        Numeric(18, 2),
        nullable=False,
    )

    total_price = Column(
        Numeric(18, 2),
        nullable=False,
    )

    quotation = relationship("Quotation",back_populates="items")

    rfq_item = relationship("RFQItem")