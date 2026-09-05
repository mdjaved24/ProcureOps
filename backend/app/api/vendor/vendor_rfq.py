from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from app.core.dependencies import get_db
from app.models.vendor.vendor_user import VendorUser
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation_requests.rfq_vendor import RFQVendor, RFQVendorStatus
from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.quotation.quotation_item import QuotationItem
from app.models.quotation_requests.rfq_item import RFQItem
from app.schemas.quotation_requests.rfq_schema import RFQResponse
from app.core.vendor_dependencies import get_current_vendor_user
from pydantic import BaseModel, Field
from typing import Optional as OptionalType


# ============================================================
# QUOTATION SUBMISSION SCHEMA
# ============================================================

class QuotationItemSubmit(BaseModel):
    rfq_item_id: int
    unit_price: float = Field(gt=0)


class QuotationSubmitRequest(BaseModel):
    rfq_id: int
    currency: str = "INR"
    tax_amount: float = 0.0
    valid_until: OptionalType[str] = None
    notes: OptionalType[str] = None
    items: List[QuotationItemSubmit]


class VendorRFQResponse(RFQResponse):
    """Extended RFQ response with vendor-specific fields"""
    has_submitted_quotation: bool = False
    quotation_id: Optional[int] = None
    quotation_status: Optional[str] = None


vendor_rfq_router = APIRouter(
    prefix="/vendor/rfqs",
    tags=["Vendor - RFQs"],
)


@vendor_rfq_router.get(
    "",
    response_model=List[VendorRFQResponse],
)
def get_vendor_rfqs(
    status_filter: Optional[RFQStatus] = Query(
        default=None,
        description="Filter by RFQ status",
    ),
    db: Session = Depends(get_db),
    vendor_user: VendorUser = Depends(get_current_vendor_user),
):
    """
    Get all RFQs that this vendor is invited to.
    Only returns RFQs where the vendor has NOT already submitted a quotation.
    """
    # Get RFQ Vendors for this vendor
    rfq_vendors = db.query(RFQVendor).filter(
        RFQVendor.vendor_id == vendor_user.vendor_id
    ).all()
    
    if not rfq_vendors:
        return []
    
    rfq_ids = [rv.rfq_id for rv in rfq_vendors]
    
    if not rfq_ids:
        return []
    
    # Get RFQs with items and vendors loaded
    query = db.query(RFQ).options(
        joinedload(RFQ.items),
        joinedload(RFQ.vendors),
    ).filter(RFQ.id.in_(rfq_ids))
    
    if status_filter:
        query = query.filter(RFQ.status == status_filter.value)
    
    rfqs = query.order_by(RFQ.created_at.desc()).all()
    
    # Filter out RFQs where vendor has already submitted a quotation
    result = []
    for rfq in rfqs:
        # Find the RFQVendor record for this vendor
        rfq_vendor = next(
            (rv for rv in rfq.vendors if rv.vendor_id == vendor_user.vendor_id),
            None
        )
        
        has_submitted = False
        quotation_id = None
        quotation_status = None
        
        if rfq_vendor:
            # Check if there's a quotation for this RFQ Vendor
            quotation = db.query(Quotation).filter(
                Quotation.rfq_vendor_id == rfq_vendor.id,
                Quotation.status == QuotationStatus.SUBMITTED.value
            ).first()
            
            if quotation:
                has_submitted = True
                quotation_id = quotation.id
                # quotation.status is already a string, not an enum
                quotation_status = quotation.status
        
        # Only include RFQs where vendor has NOT submitted a quotation
        # OR if the RFQ is CLOSED (for historical view)
        if not has_submitted or rfq.status == RFQStatus.CLOSED.value:
            # Create response with vendor-specific fields
            rfq_dict = {
                "id": rfq.id,
                "rfq_number": rfq.rfq_number,
                "purchase_request_id": rfq.purchase_request_id,
                "title": rfq.title,
                "description": rfq.description,
                "status": rfq.status,
                "issue_date": rfq.issue_date,
                "submission_deadline": rfq.submission_deadline,
                "created_by": rfq.created_by,
                "created_at": rfq.created_at,
                "updated_at": rfq.updated_at,
                "items": rfq.items,
                "vendors": rfq.vendors,
                "has_submitted_quotation": has_submitted,
                "quotation_id": quotation_id,
                "quotation_status": quotation_status,
            }
            result.append(VendorRFQResponse(**rfq_dict))
    
    return result


@vendor_rfq_router.get(
    "/{rfq_id}",
    response_model=RFQResponse,
)
def get_vendor_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    vendor_user: VendorUser = Depends(get_current_vendor_user),
):
    """
    Get a specific RFQ that this vendor is invited to.
    """
    # Check if vendor is invited to this RFQ
    rfq_vendor = db.query(RFQVendor).filter(
        RFQVendor.rfq_id == rfq_id,
        RFQVendor.vendor_id == vendor_user.vendor_id
    ).first()
    
    if not rfq_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found or you are not invited"
        )
    
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    
    return rfq


@vendor_rfq_router.post(
    "/{rfq_id}/submit-quotation",
    status_code=status.HTTP_201_CREATED,
)
def submit_quotation(
    rfq_id: int,
    request: QuotationSubmitRequest,
    db: Session = Depends(get_db),
    vendor_user: VendorUser = Depends(get_current_vendor_user),
):
    """
    Submit a quotation for an RFQ.
    """
    # Check if vendor is invited to this RFQ
    rfq_vendor = db.query(RFQVendor).filter(
        RFQVendor.rfq_id == rfq_id,
        RFQVendor.vendor_id == vendor_user.vendor_id
    ).first()
    
    if not rfq_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found or you are not invited"
        )
    
    # Check if RFQ is still open
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    
    if rfq.status != RFQStatus.ISSUED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="RFQ is not open for quotations"
        )
    
    # Check if vendor already submitted a quotation for this RFQ
    existing_quotation = db.query(Quotation).filter(
        Quotation.rfq_vendor_id == rfq_vendor.id,
        Quotation.status == QuotationStatus.SUBMITTED.value
    ).first()
    
    if existing_quotation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted a quotation for this RFQ"
        )
    
    # Validate that all RFQ items are quoted
    rfq_items = db.query(RFQItem).filter(RFQItem.rfq_id == rfq_id).all()
    rfq_item_ids = set(item.id for item in rfq_items)
    submitted_item_ids = set(item.rfq_item_id for item in request.items)
    
    if rfq_item_ids != submitted_item_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide prices for all items"
        )
    
    # Calculate totals
    subtotal = Decimal('0.00')
    quotation_items_data = []
    
    for item_data in request.items:
        rfq_item = next((item for item in rfq_items if item.id == item_data.rfq_item_id), None)
        if not rfq_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid RFQ item ID: {item_data.rfq_item_id}"
            )
        
        quantity = Decimal(str(rfq_item.quantity))
        unit_price = Decimal(str(item_data.unit_price))
        total_price = quantity * unit_price
        subtotal += total_price
        
        quotation_items_data.append({
            "rfq_item": rfq_item,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
        })
    
    tax_amount = Decimal(str(request.tax_amount))
    total_amount = subtotal + tax_amount
    
    # Generate quotation number
    last_quotation = db.query(Quotation).order_by(Quotation.id.desc()).first()
    next_number = (last_quotation.id + 1) if last_quotation else 1
    quotation_number = f"QT-{next_number:06d}"
    
    # Create Quotation
    quotation = Quotation(
        rfq_vendor_id=rfq_vendor.id,
        quotation_number=quotation_number,
        status=QuotationStatus.SUBMITTED.value,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=request.currency.upper(),
        valid_until=datetime.fromisoformat(request.valid_until) if request.valid_until else None,
        notes=request.notes,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(quotation)
    db.flush()
    
    # Create Quotation Items
    for item_data in quotation_items_data:
        quotation_item = QuotationItem(
            quotation_id=quotation.id,
            rfq_item_id=item_data["rfq_item"].id,
            item_name=item_data["rfq_item"].item_name,
            description=item_data["rfq_item"].description,
            quantity=item_data["quantity"],
            unit=item_data["rfq_item"].unit,
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"],
        )
        db.add(quotation_item)
    
    # Update RFQ Vendor status to RESPONDED
    rfq_vendor.status = RFQVendorStatus.RESPONDED.value
    
    db.commit()
    db.refresh(quotation)
    
    return {
        "message": "Quotation submitted successfully",
        "quotation_id": quotation.id,
        "quotation_number": quotation.quotation_number,
        "rfq_id": rfq_id,
        "vendor_id": vendor_user.vendor_id
    }