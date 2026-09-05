from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.quotation.quotation import QuotationStatus


class QuotationItemCreate(BaseModel):
    rfq_item_id: int
    unit_price: Decimal = Field(
        gt=0, max_digits=18, 
        decimal_places=2
        )


class QuotationCreate(BaseModel):
    rfq_vendor_id: int
    currency: str = Field(
        default="INR", 
        min_length=3, 
        max_length=10
        )
    tax_amount: Decimal = Field(
        default=Decimal("0.00"), 
        ge=0, max_digits=18, 
        decimal_places=2
        )
    valid_until: datetime | None = None
    notes: str | None = Field(
        default=None, 
        max_length=5000
        )
    items: List[QuotationItemCreate] = Field(min_length=1)


class QuotationItemUpdate(BaseModel):
    rfq_item_id: int
    unit_price: Decimal = Field(gt=0, 
                                max_digits=18, 
                                decimal_places=2
                                )


class QuotationUpdate(BaseModel):
    currency: str | None = Field(
                            default=None, 
                            min_length=3, 
                            max_length=10
                            )
    tax_amount: Decimal | None = Field(
                            default=None, 
                            ge=0, 
                            max_digits=18, 
                            decimal_places=2
                            )
    valid_until: datetime | None = None
    notes: str | None = Field(
                            default=None, 
                            max_length=5000
                            )
    items: List[QuotationItemUpdate] | None = Field(
                            default=None, 
                            min_length=1
                            )


class QuotationSubmitRequest(BaseModel):
    confirm_submission: bool = True


class QuotationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quotation_id: int
    rfq_item_id: int
    item_name: str
    description: str | None
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_price: Decimal


class QuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_vendor_id: int
    quotation_number: str
    status: QuotationStatus
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    valid_until: datetime | None
    notes: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: List[QuotationItemResponse] = []


class QuotationListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quotation_number: str
    rfq_vendor_id: int
    rfq_id: Optional[int] = None
    rfq_number: Optional[str] = None
    vendor_name: Optional[str] = None
    status: QuotationStatus
    currency: str
    total_amount: Decimal
    submitted_at: datetime | None
    created_at: datetime