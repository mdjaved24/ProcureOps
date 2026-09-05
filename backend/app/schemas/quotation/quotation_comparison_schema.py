from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel


class QuotationItemPriceResponse(BaseModel):
    quotation_id: int
    vendor_id: int
    vendor_name: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


class RFQItemComparisonResponse(BaseModel):
    rfq_item_id: int
    item_name: str
    description: str | None
    quantity: Decimal
    unit: str
    prices: list[QuotationItemPriceResponse]


class QuotationComparisonSummary(BaseModel):
    rank: int
    quotation_id: int
    vendor_id: int
    vendor_name: str
    vendor_code: str
    total_amount: Decimal
    currency: str
    delivery_days: int | None
    payment_terms: str | None
    validity_date: datetime | None


class RFQQuotationComparisonResponse(BaseModel):
    rfq_id: int
    rfq_number: str
    title: str
    quotation_count: int
    quotations: list[QuotationComparisonSummary]
    item_comparison: list[RFQItemComparisonResponse]