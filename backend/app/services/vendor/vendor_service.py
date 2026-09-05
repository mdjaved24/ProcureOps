from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.models.audit.audit_log import AuditActorType, AuditLog
from app.models.identity.user import User
from app.models.vendor.vendor import VendorStatus, Vendor
from app.schemas.vendor.vendor_schema import (
    VendorCreate,
    VendorResponse,
    VendorStatusUpdate,
    VendorUpdate
)
from app.services.audit.audit_service import AuditService


VALID_VENDOR_STATUS_TRANSITIONS = {
    VendorStatus.ACTIVE: {
        VendorStatus.INACTIVE,
        VendorStatus.BLOCKED,
    },
    VendorStatus.INACTIVE: {
        VendorStatus.ACTIVE,
    },
    VendorStatus.BLOCKED: {
        VendorStatus.ACTIVE,
        VendorStatus.INACTIVE,
    },
}


class VendorService:

    @staticmethod
    def create_vendor(
        db: Session,
        current_user: User,
        request: VendorCreate
    ):
        normalized_vendor_code = request.vendor_code.upper().strip()

        vendor = db.query(Vendor).filter(
            Vendor.vendor_code == normalized_vendor_code
        ).first()

        if vendor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor with the given vendor code already exists"
            )

        normalized_tax_id = request.tax_id.upper().strip()

        vendor = db.query(Vendor).filter(
            Vendor.tax_id == normalized_tax_id
        ).first()

        if vendor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tax id is already taken"
            )

        email = request.email.lower()

        if not request.phone.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide a valid phone number"
            )

        vendor = Vendor(
            vendor_code=normalized_vendor_code,
            name=request.name,
            description=request.description,
            email=email,
            phone=request.phone,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            postal_code=request.postal_code,
            tax_id=normalized_tax_id
        )

        db.add(vendor)
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="VENDOR_CREATED",
            resource_type="VENDOR",
            resource_id=vendor.id,
            previous_state=None,
            new_state={
                "vendor_code": vendor.vendor_code,
                "name": vendor.name,
                "email": vendor.email,
                "phone": vendor.phone,
                "tax_id": vendor.tax_id,
                "status": vendor.status,
            },
            metadata={
                "source": "VENDOR_MANAGEMENT",
            },
        )

        try:
            db.commit()
            db.refresh(vendor)
            return vendor
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_vendor_by_id(
        db: Session,
        vendor_id: int
    ):
        vendor = db.query(Vendor).filter(
            Vendor.id == vendor_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        return vendor

    @staticmethod
    def get_vendor_by_code(
        db: Session,
        vendor_code: int
    ):
        normalized_vendor_code = vendor_code.upper().strip()

        vendor = db.query(Vendor).filter(
            Vendor.vendor_code == normalized_vendor_code
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        return vendor

    @staticmethod
    def update_vendor(
        db: Session,
        vendor_id: int,
        current_user: User,
        request: VendorUpdate,
    ) -> Vendor:
        vendor = db.query(Vendor).filter(
            Vendor.id == vendor_id
        ).with_for_update().first()

        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )

        previous_state = {
            "vendor_code": vendor.vendor_code,
            "name": vendor.name,
            "description": vendor.description,
            "email": vendor.email,
            "phone": vendor.phone,
            "address": vendor.address,
            "city": vendor.city,
            "state": vendor.state,
            "country": vendor.country,
            "postal_code": vendor.postal_code,
            "tax_id": vendor.tax_id,
            "status": vendor.status,
        }

        update_data = request.model_dump(exclude_unset=True)

        if "vendor_code" in update_data:
            normalized_vendor_code = update_data["vendor_code"].upper().strip()

            existing_vendor = db.query(Vendor).filter(
                Vendor.vendor_code == normalized_vendor_code,
                Vendor.id != vendor.id,
            ).first()

            if existing_vendor is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Vendor with the given vendor code already exists"
                )

            update_data["vendor_code"] = normalized_vendor_code

        if "tax_id" in update_data and update_data["tax_id"] is not None:
            normalized_tax_id = update_data["tax_id"].upper().strip()

            existing_vendor = db.query(Vendor).filter(
                Vendor.tax_id == normalized_tax_id,
                Vendor.id != vendor.id,
            ).first()

            if existing_vendor is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tax ID is already taken",
                )

            update_data["tax_id"] = normalized_tax_id

        if "email" in update_data and update_data["email"] is not None:
            normalized_email = update_data["email"].lower().strip()

            existing_vendor = db.query(Vendor).filter(
                func.lower(Vendor.email) == normalized_email,
                Vendor.id != vendor.id,
            ).first()

            if existing_vendor is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already taken",
                )

            update_data["email"] = normalized_email

        if "phone" in update_data and update_data["phone"] is not None:
            phone = update_data["phone"].strip()

            if not phone.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide a valid phone number"
                )

            update_data["phone"] = phone

        for field, value in update_data.items():
            setattr(vendor, field, value)

        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="VENDOR_UPDATED",
            resource_type="VENDOR",
            resource_id=vendor.id,
            previous_state=previous_state,
            new_state={
                "vendor_code": vendor.vendor_code,
                "name": vendor.name,
                "description": vendor.description,
                "email": vendor.email,
                "phone": vendor.phone,
                "address": vendor.address,
                "city": vendor.city,
                "state": vendor.state,
                "country": vendor.country,
                "postal_code": vendor.postal_code,
                "tax_id": vendor.tax_id,
                "status": vendor.status,
            },
            metadata={
                "updated_fields": list(update_data.keys()),
                "source": "VENDOR_MANAGEMENT",
            },
        )

        try:
            db.commit()
            db.refresh(vendor)
            return vendor
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_vendor_status(
        db: Session,
        current_user: User,
        vendor_id: int,
        request: VendorStatusUpdate
    ):
        vendor = db.query(Vendor).filter(
            Vendor.id == vendor_id
        ).with_for_update().first()

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        previous_state = {
            "vendor_code": vendor.vendor_code,
            "name": vendor.name,
            "description": vendor.description,
            "email": vendor.email,
            "phone": vendor.phone,
            "address": vendor.address,
            "city": vendor.city,
            "state": vendor.state,
            "country": vendor.country,
            "postal_code": vendor.postal_code,
            "tax_id": vendor.tax_id,
            "status": vendor.status,
        }

        current_status = VendorStatus(vendor.status)
        requested_status = request.status
        allowed_transitions = VALID_VENDOR_STATUS_TRANSITIONS.get(current_status, set())

        if requested_status not in allowed_transitions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid vendor status transition: {current_status.value} → {requested_status.value}",
            )

        vendor.status = request.status.value
        db.flush()

        AuditService.log(
            db=db,
            actor_type=AuditActorType.USER,
            actor_id=current_user.id,
            action="VENDOR_STATUS_UPDATED",
            resource_type="VENDOR",
            resource_id=vendor.id,
            previous_state=previous_state,
            new_state={
                "vendor_code": vendor.vendor_code,
                "name": vendor.name,
                "description": vendor.description,
                "email": vendor.email,
                "phone": vendor.phone,
                "address": vendor.address,
                "city": vendor.city,
                "state": vendor.state,
                "country": vendor.country,
                "postal_code": vendor.postal_code,
                "tax_id": vendor.tax_id,
                "status": vendor.status,
            },
            metadata={
                "updated_fields": ["status"],
                "source": "VENDOR_MANAGEMENT",
            },
        )

        try:
            db.commit()
            db.refresh(vendor)
            return vendor
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_vendors(
        db: Session,
        status_filter: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        query = db.query(Vendor)

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Vendor.vendor_code.ilike(search_pattern),
                    Vendor.name.ilike(search_pattern),
                    Vendor.email.ilike(search_pattern),
                    Vendor.phone.ilike(search_pattern),
                    Vendor.tax_id.ilike(search_pattern),
                    Vendor.city.ilike(search_pattern),
                    Vendor.country.ilike(search_pattern),
                )
            )

        if status_filter:
            query = query.filter(Vendor.status == status_filter.value)

        total = query.count()

        vendors = (
            query
            .order_by(desc(Vendor.id))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "vendors": vendors,
        }