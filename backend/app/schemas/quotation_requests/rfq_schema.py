from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.quotation_requests.rfq import RFQStatus
from app.models.quotation_requests.rfq_vendor import (
    RFQVendorStatus,
)


class RFQCreate(BaseModel):

    purchase_request_id: int
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    submission_deadline: datetime


class RFQUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    submission_deadline: datetime | None = None


class RFQVendorAdd(BaseModel):
    vendor_id: int



class RFQItemResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    rfq_id: int
    purchase_request_item_id: int
    item_name: str
    description: str | None
    quantity: Decimal
    unit: str



class RFQVendorResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    rfq_id: int
    vendor_id: int
    status: RFQVendorStatus
    invited_at: datetime



class RFQResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    rfq_number: str
    purchase_request_id: int
    title: str
    description: str | None
    status: RFQStatus
    issue_date: datetime | None
    submission_deadline: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[RFQItemResponse] = []
    vendors: list[RFQVendorResponse] = []
