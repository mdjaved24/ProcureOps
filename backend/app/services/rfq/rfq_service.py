from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.models.audit.audit_log import AuditActorType
from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequest, PurchaseRequestStatus
from app.models.procurement.purchase_request_item import PurchaseRequestItem
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation_requests.rfq_item import RFQItem
from app.models.quotation_requests.rfq_vendor import RFQVendor, RFQVendorStatus
from app.models.vendor.vendor import Vendor, VendorStatus
from app.schemas.quotation_requests.rfq_schema import RFQCreate, RFQUpdate
from app.services.audit.audit_service import AuditService
from app.services.rfq.rfq_workflow import VALID_RFQ_TRANSITIONS


class RFQService:

    @staticmethod
    def create_rfq(
        db: Session,
        current_user: User,
        request: RFQCreate,
    ) -> RFQ:
        purchase_request = (
            db.query(PurchaseRequest)
            .filter(PurchaseRequest.id == request.purchase_request_id)
            .with_for_update()
            .first()
        )

        if purchase_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found",
            )

        if purchase_request.status != PurchaseRequestStatus.APPROVED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="RFQ can only be created for an approved purchase request",
            )

        existing_rfq = (
            db.query(RFQ)
            .filter(
                RFQ.purchase_request_id == purchase_request.id,
                RFQ.status.in_([
                    RFQStatus.DRAFT.value,
                    RFQStatus.ISSUED.value,
                ]),
            )
            .first()
        )

        if existing_rfq:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active RFQ already exists for this purchase request",
            )

        items = (
            db.query(PurchaseRequestItem)
            .filter(PurchaseRequestItem.purchase_request_id == purchase_request.id)
            .with_for_update()
            .all()
        )

        if not items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot create RFQ because the purchase request has no items",
            )

        last_rfq = db.query(RFQ).order_by(RFQ.id.desc()).first()
        next_number = last_rfq.id + 1 if last_rfq else 1
        rfq_number = f"RFQ-{next_number:06d}"

        rfq = RFQ(
            rfq_number=rfq_number,
            purchase_request_id=purchase_request.id,
            title=request.title.strip(),
            description=request.description,
            status=RFQStatus.DRAFT.value,
            submission_deadline=request.submission_deadline,
            created_by=current_user.id,
        )

        db.add(rfq)
        db.flush()

        for purchase_request_item in items:
            rfq_item = RFQItem(
                rfq_id=rfq.id,
                purchase_request_item_id=purchase_request_item.id,
                item_name=purchase_request_item.item_name,
                description=purchase_request_item.description,
                quantity=purchase_request_item.quantity,
                unit=purchase_request_item.unit,
            )
            db.add(rfq_item)

        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_CREATED",
            resource_type="RFQ",
            resource_id=rfq.id,
            previous_state=None,
            new_state={
                "rfq_number": rfq.rfq_number,
                "purchase_request_id": rfq.purchase_request_id,
                "title": rfq.title,
                "status": rfq.status,
                "submission_deadline": rfq.submission_deadline.isoformat() if rfq.submission_deadline else None,
            },
            metadata={
                "item_count": len(purchase_request.items),
                "source": "RFQ_MANAGEMENT",
            },
        )

        try:
            db.commit()
            db.refresh(rfq)
        except Exception:
            db.rollback()
            raise

        return rfq

    @staticmethod
    def get_rfq_by_id(
        db: Session,
        rfq_id: int,
    ) -> RFQ:
        rfq = (
            db.query(RFQ)
            .options(
                joinedload(RFQ.items),
                joinedload(RFQ.vendors),
                joinedload(RFQ.purchase_request),
            )
            .filter(RFQ.id == rfq_id)
            .first()
        )

        if rfq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RFQ not found",
            )

        return rfq

    @staticmethod
    def update_rfq(
        db: Session,
        current_user: User,
        rfq_id: int,
        request: RFQUpdate,
    ) -> RFQ:
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

        if rfq.status != RFQStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft RFQs can be updated",
            )

        previous_state = {
            "title": rfq.title,
            "description": rfq.description,
            "submission_deadline": rfq.submission_deadline.isoformat() if rfq.submission_deadline else None,
            "status": rfq.status,
        }

        updated_fields = []

        if request.title is not None:
            title = request.title.strip()
            if title != rfq.title:
                rfq.title = title
                updated_fields.append("title")

        if request.description != rfq.description:
            rfq.description = request.description
            updated_fields.append("description")

        if request.submission_deadline is not None:
            if request.submission_deadline != rfq.submission_deadline:
                rfq.submission_deadline = request.submission_deadline
                updated_fields.append("submission_deadline")

        if not updated_fields:
            return rfq

        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_UPDATED",
            resource_type="RFQ",
            resource_id=rfq.id,
            previous_state=previous_state,
            new_state={
                "title": rfq.title,
                "description": rfq.description,
                "submission_deadline": rfq.submission_deadline.isoformat() if rfq.submission_deadline else None,
                "status": rfq.status,
            },
            metadata={
                "updated_fields": updated_fields,
                "source": "RFQ_MANAGEMENT",
            },
        )

        try:
            db.commit()
            db.refresh(rfq)
        except Exception:
            db.rollback()
            raise

        return rfq

    @staticmethod
    def add_vendor(
        db: Session,
        rfq_id: int,
        vendor_id: int,
        current_user: User,
    ) -> RFQ:
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

        if rfq.status != RFQStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot add vendors to RFQ with status {rfq.status}",
            )

        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )

        existing_rfq_vendor = (
            db.query(RFQVendor)
            .filter(
                RFQVendor.rfq_id == rfq_id,
                RFQVendor.vendor_id == vendor_id,
            )
            .first()
        )

        if existing_rfq_vendor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor already added to this RFQ",
            )

        rfq_vendor = RFQVendor(
            rfq_id=rfq_id,
            vendor_id=vendor_id,
            status=RFQVendorStatus.INVITED.value,
        )

        db.add(rfq_vendor)
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_VENDOR_ADDED",
            resource_type="RFQ",
            resource_id=rfq.id,
            metadata={
                "vendor_id": vendor_id,
                "vendor_name": vendor.name,
            },
        )

        db.commit()
        rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()

        return rfq

    @staticmethod
    def remove_vendor(
        db: Session,
        current_user: User,
        rfq_id: int,
        vendor_id: int,
    ) -> None:
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

        if rfq.status != RFQStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendors can only be removed from a draft RFQ",
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor is not assigned to this RFQ",
            )

        previous_state = {
            "rfq_id": rfq_vendor.rfq_id,
            "vendor_id": rfq_vendor.vendor_id,
            "status": rfq_vendor.status,
        }

        rfq_vendor_id = rfq_vendor.id

        db.delete(rfq_vendor)
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="VENDOR_REMOVED_FROM_RFQ",
            resource_type="RFQ_VENDOR",
            resource_id=rfq_vendor_id,
            previous_state=previous_state,
            new_state=None,
            metadata={
                "rfq_id": rfq.id,
                "vendor_id": vendor_id,
                "source": "RFQ_MANAGEMENT",
            },
        )

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_rfqs(
        db: Session,
        status_filter: Optional[RFQStatus] = None,
        purchase_request_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[RFQ]:
        query = db.query(RFQ).options(
            joinedload(RFQ.items),
            joinedload(RFQ.vendors),
        )

        if status_filter is not None:
            query = query.filter(RFQ.status == status_filter.value)

        if purchase_request_id is not None:
            query = query.filter(RFQ.purchase_request_id == purchase_request_id)

        return (
            query
            .order_by(desc(RFQ.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def issue_rfq(
        db: Session,
        rfq_id: int,
        current_user: User,
    ) -> RFQ:
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

        current_status = RFQStatus(rfq.status)

        if RFQStatus.ISSUED not in VALID_RFQ_TRANSITIONS.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"RFQ cannot be issued from status {rfq.status}",
            )

        rfq_items = (
            db.query(RFQItem)
            .filter(RFQItem.rfq_id == rfq_id)
            .all()
        )

        if not rfq_items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="RFQ cannot be issued without items",
            )

        rfq_vendors = (
            db.query(RFQVendor)
            .filter(RFQVendor.rfq_id == rfq_id)
            .all()
        )

        if not rfq_vendors:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="RFQ cannot be issued without vendors",
            )

        if rfq.submission_deadline is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission deadline is required before issuing RFQ",
            )

        current_time = datetime.now(timezone.utc)
        deadline = rfq.submission_deadline

        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        if deadline <= current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission deadline must be in the future",
            )

        previous_state = {
            "status": rfq.status,
            "issue_date": rfq.issue_date.isoformat() if rfq.issue_date else None,
        }

        rfq.status = RFQStatus.ISSUED.value
        rfq.issue_date = current_time

        for rfq_vendor in rfq_vendors:
            rfq_vendor.status = RFQVendorStatus.INVITED.value

        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_ISSUED",
            resource_type="RFQ",
            resource_id=rfq.id,
            previous_state=previous_state,
            new_state={
                "status": rfq.status,
                "issue_date": rfq.issue_date.isoformat(),
            },
            metadata={
                "vendor_count": len(rfq_vendors),
                "item_count": len(rfq_items),
                "source": "RFQ_MANAGEMENT",
            },
        )

        try:
            db.commit()
            rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
        except Exception:
            db.rollback()
            raise

        return rfq

    @staticmethod
    def close_rfq(
        db: Session,
        rfq_id: int,
        current_user: User,
    ) -> RFQ:
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

        current_status = RFQStatus(rfq.status)

        if RFQStatus.CLOSED not in VALID_RFQ_TRANSITIONS.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"RFQ cannot be closed from status {rfq.status}",
            )

        previous_state = {"status": rfq.status}

        rfq.status = RFQStatus.CLOSED.value
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_CLOSED",
            resource_type="RFQ",
            resource_id=rfq.id,
            previous_state=previous_state,
            new_state={"status": rfq.status},
            metadata={"source": "RFQ_MANAGEMENT"},
        )

        try:
            db.commit()
            db.refresh(rfq)
        except Exception:
            db.rollback()
            raise

        return rfq

    @staticmethod
    def cancel_rfq(
        db: Session,
        rfq_id: int,
        current_user: User,
    ) -> RFQ:
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

        current_status = RFQStatus(rfq.status)

        if RFQStatus.CANCELLED not in VALID_RFQ_TRANSITIONS.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"RFQ cannot be cancelled from status {rfq.status}",
            )

        previous_state = {"status": rfq.status}

        rfq.status = RFQStatus.CANCELLED.value
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="RFQ_CANCELLED",
            resource_type="RFQ",
            resource_id=rfq.id,
            previous_state=previous_state,
            new_state={"status": rfq.status},
            metadata={"source": "RFQ_MANAGEMENT"},
        )

        try:
            db.commit()
            db.refresh(rfq)
        except Exception:
            db.rollback()
            raise

        return rfq