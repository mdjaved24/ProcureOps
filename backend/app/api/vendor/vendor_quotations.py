from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.dependencies import get_db
from app.models.vendor.vendor_user import VendorUser
from app.models.quotation.quotation import Quotation
from app.models.quotation.quotation_item import QuotationItem
from app.models.quotation_requests.rfq_vendor import RFQVendor
from app.schemas.quotation.quotation_schema import QuotationResponse
from app.core.vendor_dependencies import get_current_vendor_user


vendor_quotation_router = APIRouter(
    prefix="/vendor/quotations",
    tags=["Vendor - Quotations"],
)


@vendor_quotation_router.get(
    "",
    response_model=List[QuotationResponse],
)
def get_vendor_quotations(
    db: Session = Depends(get_db),
    vendor_user: VendorUser = Depends(get_current_vendor_user),
):
    """
    Get all quotations submitted by this vendor.
    """
    # Get RFQ Vendors for this vendor
    rfq_vendors = db.query(RFQVendor).filter(
        RFQVendor.vendor_id == vendor_user.vendor_id
    ).all()
    
    if not rfq_vendors:
        return []
    
    rfq_vendor_ids = [rv.id for rv in rfq_vendors]
    
    # Get quotations with items loaded
    quotations = db.query(Quotation).options(
        joinedload(Quotation.items)
    ).filter(
        Quotation.rfq_vendor_id.in_(rfq_vendor_ids)
    ).order_by(Quotation.created_at.desc()).all()
    
    return quotations