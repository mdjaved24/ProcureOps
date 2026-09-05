from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.audit.audit_log import AuditActorType
from app.models.identity.user import User
from app.models.vendor.vendor import Vendor, VendorStatus
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation_requests.rfq_item import RFQItem
from app.models.quotation_requests.rfq_vendor import RFQVendor, RFQVendorStatus
from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.quotation.quotation_item import QuotationItem
from app.schemas.quotation.quotation_schema import QuotationCreate, QuotationUpdate, QuotationListResponse
from app.services.audit.audit_service import AuditService


class QuotationService:

    @staticmethod
    def submit_quotation(
        db: Session,
        rfq_id: int,
        vendor_id: int,
        request: QuotationCreate,
        current_user: User,
    ) -> Quotation:
        # Lock RFQ
        rfq = (
            db.query(RFQ)
            .filter(RFQ.id == rfq_id)
            .with_for_update()
            .first()
        )

        if rfq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RFQ not found",
            )

        if rfq.status != RFQStatus.ISSUED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quotation can only be submitted for an issued RFQ",
            )

        vendor = (
            db.query(Vendor)
            .filter(Vendor.id == vendor_id)
            .first()
        )

        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )

        if vendor.status != VendorStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inactive vendor cannot submit a quotation",
            )

        rfq_vendor = (
            db.query(RFQVendor)
            .filter(
                RFQVendor.rfq_id == rfq_id,
                RFQVendor.vendor_id == vendor_id,
            )
            .with_for_update()
            .first()
        )

        if rfq_vendor is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendor was not invited to this RFQ",
            )

        if rfq_vendor.status != RFQVendorStatus.INVITED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor is not eligible to submit a quotation for this RFQ",
            )

        existing_quotation = (
            db.query(Quotation)
            .filter(Quotation.rfq_vendor_id == rfq_vendor.id)
            .first()
        )

        if existing_quotation is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor has already submitted a quotation for this RFQ",
            )

        rfq_items = (
            db.query(RFQItem)
            .filter(RFQItem.rfq_id == rfq_id)
            .all()
        )

        rfq_item_ids = {item.id for item in rfq_items}
        submitted_item_ids = {item.rfq_item_id for item in request.items}

        if rfq_item_ids != submitted_item_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quotation must contain exactly all RFQ items",
            )

        if len(submitted_item_ids) != len(request.items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate RFQ items found in quotation",
            )

        rfq_items_map = {item.id: item for item in rfq_items}

        for item_data in request.items:
            rfq_item = rfq_items_map.get(item_data.rfq_item_id)
            if rfq_item is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid RFQ item provided",
                )

        quotation_subtotal = Decimal("0.00")
        calculated_items = []

        for item_data in request.items:
            rfq_item = rfq_items_map.get(item_data.rfq_item_id)
            quantity = rfq_item.quantity
            unit_price = item_data.unit_price
            item_total = quantity * unit_price

            quotation_subtotal += item_total

            calculated_items.append({
                "rfq_item_id": item_data.rfq_item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": item_total,
            })

        tax_amount = request.tax_amount if hasattr(request, 'tax_amount') else Decimal("0.00")
        quotation_total = quotation_subtotal + tax_amount

        last_quotation = (
            db.query(Quotation)
            .order_by(Quotation.id.desc())
            .first()
        )

        next_number = last_quotation.id + 1 if last_quotation else 1
        quotation_number = f"QT-{next_number:06d}"

        quotation = Quotation(
            rfq_vendor_id=rfq_vendor.id,
            quotation_number=quotation_number,
            status=QuotationStatus.SUBMITTED.value,
            subtotal=quotation_subtotal,
            tax_amount=tax_amount,
            total_amount=quotation_total,
            currency=request.currency.upper(),
            valid_until=request.valid_until if hasattr(request, 'valid_until') else None,
            notes=request.notes if hasattr(request, 'notes') else None,
            submitted_at=datetime.now(timezone.utc),
        )

        db.add(quotation)
        db.flush()

        for item_data in calculated_items:
            rfq_item = rfq_items_map.get(item_data["rfq_item_id"])
            quotation_item = QuotationItem(
                quotation_id=quotation.id,
                rfq_item_id=item_data["rfq_item_id"],
                item_name=rfq_item.item_name,
                description=rfq_item.description,
                quantity=item_data["quantity"],
                unit=rfq_item.unit,
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
            )
            db.add(quotation_item)

        rfq_vendor.status = RFQVendorStatus.RESPONDED.value
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="QUOTATION_SUBMITTED",
            resource_type="QUOTATION",
            resource_id=quotation.id,
            previous_state=None,
            new_state={
                "rfq_vendor_id": quotation.rfq_vendor_id,
                "status": quotation.status,
                "total_amount": str(quotation.total_amount),
                "currency": quotation.currency,
            },
            metadata={
                "rfq_number": rfq.rfq_number,
                "vendor_code": vendor.vendor_code,
                "item_count": len(request.items),
            },
        )

        try:
            db.commit()
            db.refresh(quotation)
        except Exception:
            db.rollback()
            raise

        return quotation

    @staticmethod
    def get_quotation_by_id(
        db: Session,
        quotation_id: int,
    ) -> Quotation:
        quotation = (
            db.query(Quotation)
            .options(joinedload(Quotation.items))
            .filter(Quotation.id == quotation_id)
            .first()
        )

        if quotation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found",
            )

        return quotation

    @staticmethod
    def list_all_quotations(
        db: Session,
    ) -> List[QuotationListResponse]:
        quotations = db.query(Quotation).order_by(Quotation.created_at.desc()).all()
        result = []

        for quotation in quotations:
            rfq_vendor = db.query(RFQVendor).filter(
                RFQVendor.id == quotation.rfq_vendor_id
            ).first()

            vendor_name = None
            vendor_id = None
            rfq_number = None
            rfq_id = None

            if rfq_vendor:
                vendor_id = rfq_vendor.vendor_id
                vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()
                if vendor:
                    vendor_name = vendor.name

                rfq = db.query(RFQ).filter(RFQ.id == rfq_vendor.rfq_id).first()
                if rfq:
                    rfq_number = rfq.rfq_number
                    rfq_id = rfq.id

            result.append(QuotationListResponse(
                id=quotation.id,
                quotation_number=quotation.quotation_number,
                rfq_vendor_id=quotation.rfq_vendor_id,
                rfq_id=rfq_id,
                rfq_number=rfq_number,
                vendor_name=vendor_name,
                vendor_id=vendor_id,
                status=quotation.status,
                currency=quotation.currency,
                total_amount=quotation.total_amount,
                subtotal=quotation.subtotal,
                tax_amount=quotation.tax_amount,
                submitted_at=quotation.submitted_at,
                created_at=quotation.created_at,
            ))

        return result

    @staticmethod
    def list_quotations_for_rfq(
        db: Session,
        rfq_id: int,
    ) -> List[QuotationListResponse]:
        rfq = (
            db.query(RFQ)
            .filter(RFQ.id == rfq_id)
            .first()
        )

        if rfq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RFQ not found",
            )

        rfq_vendors = db.query(RFQVendor).filter(RFQVendor.rfq_id == rfq_id).all()
        rfq_vendor_ids = [rv.id for rv in rfq_vendors]

        quotations = (
            db.query(Quotation)
            .filter(
                Quotation.rfq_vendor_id.in_(rfq_vendor_ids),
                Quotation.status == QuotationStatus.SUBMITTED.value
            )
            .order_by(Quotation.total_amount.asc())
            .all()
        )

        result = []

        for quotation in quotations:
            rfq_vendor = next(
                (rv for rv in rfq_vendors if rv.id == quotation.rfq_vendor_id),
                None
            )

            vendor_name = None
            vendor_id = None

            if rfq_vendor:
                vendor_id = rfq_vendor.vendor_id
                vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()
                if vendor:
                    vendor_name = vendor.name

            result.append(QuotationListResponse(
                id=quotation.id,
                quotation_number=quotation.quotation_number,
                rfq_vendor_id=quotation.rfq_vendor_id,
                rfq_id=rfq_id,
                rfq_number=rfq.rfq_number,
                vendor_name=vendor_name,
                vendor_id=vendor_id,
                status=quotation.status,
                currency=quotation.currency,
                total_amount=quotation.total_amount,
                subtotal=quotation.subtotal,
                tax_amount=quotation.tax_amount,
                submitted_at=quotation.submitted_at,
                created_at=quotation.created_at,
            ))

        return result

    @staticmethod
    def withdraw_quotation(
        db: Session,
        quotation_id: int,
        current_user: User,
    ) -> Quotation:
        quotation = (
            db.query(Quotation)
            .filter(Quotation.id == quotation_id)
            .with_for_update()
            .first()
        )

        if quotation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found",
            )

        if quotation.status != QuotationStatus.SUBMITTED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only submitted quotations can be withdrawn",
            )

        previous_state = {
            "status": quotation.status,
            "total_amount": str(quotation.total_amount),
            "currency": quotation.currency,
        }

        quotation.status = QuotationStatus.WITHDRAWN.value

        rfq_vendor = (
            db.query(RFQVendor)
            .filter(RFQVendor.id == quotation.rfq_vendor_id)
            .with_for_update()
            .first()
        )

        if rfq_vendor is not None:
            rfq_vendor.status = RFQVendorStatus.INVITED.value

        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="QUOTATION_WITHDRAWN",
            resource_type="QUOTATION",
            resource_id=quotation.id,
            previous_state=previous_state,
            new_state={
                "status": quotation.status,
                "total_amount": str(quotation.total_amount),
                "currency": quotation.currency,
            },
            metadata={
                "quotation_id": quotation.id,
                "rfq_vendor_id": quotation.rfq_vendor_id,
            },
        )

        try:
            db.commit()
            db.refresh(quotation)
        except Exception:
            db.rollback()
            raise

        return quotation