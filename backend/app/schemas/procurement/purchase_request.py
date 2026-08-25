from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRequestItemCreate(BaseModel):
    item_name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)

    quantity: Decimal = Field(gt=0)
    unit: str = Field(default="unit", min_length=1, max_length=50)

    estimated_unit_price: Decimal = Field(gt=0)


class PurchaseRequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)

    description: str | None = None

    estimated_amount: Decimal = Field(gt=0)

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    required_by_date: datetime | None = None

    items: list[PurchaseRequestItemCreate] = Field(
        min_length=1,
    )


class PurchaseRequestItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_name: str
    description: str | None
    quantity: Decimal
    unit: str
    estimated_unit_price: Decimal
    total_price: Decimal


class PurchaseRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_number: str
    title: str
    description: str | None

    requester_id: int
    department_id: int

    estimated_amount: Decimal
    currency: str
    status: str

    required_by_date: datetime | None

    created_at: datetime
    updated_at: datetime

    items: list[PurchaseRequestItemResponse]