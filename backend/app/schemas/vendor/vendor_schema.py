from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from app.models.vendor.vendor import VendorStatus


class VendorBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    email: EmailStr
    phone: str = Field(
        default=None,
        max_length=50,
    )
    address: str | None = Field(
        default=None,
        max_length=2000,
    )
    city: str | None = Field(
        default=None,
        max_length=100,
    )
    state: str | None = Field(
        default=None,
        max_length=100,
    )
    country: str | None = Field(
        default=None,
        max_length=100,
    )
    postal_code: str | None = Field(
        default=None,
        max_length=20,
    )
    tax_id: str = Field(
        default=None,
        max_length=100,
    )


class VendorCreate(VendorBase):

    vendor_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )



class VendorUpdate(BaseModel):

    vendor_code: str | None = Field(
        ...,
        min_length=2,
        max_length=50,
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=50,
    )
    address: str | None = Field(
        default=None,
        max_length=2000,
    )
    city: str | None = Field(
        default=None,
        max_length=100,
    )
    state: str | None = Field(
        default=None,
        max_length=100,
    )
    country: str | None = Field(
        default=None,
        max_length=100,
    )
    postal_code: str | None = Field(
        default=None,
        max_length=20,
    )
    tax_id: str | None = Field(
        default=None,
        max_length=100,
    )


class VendorStatusUpdate(BaseModel):
    status: VendorStatus


class VendorResponse(VendorBase):
    id: int
    vendor_code: str
    status: VendorStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
    )