from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.authorization import require_permission
from app.core.dependencies import get_current_user, get_db
from app.models.identity.user import User
from app.models.vendor.vendor import VendorStatus
from app.schemas.vendor.vendor_schema import (
    VendorCreate,
    VendorResponse,
    VendorStatusUpdate,
    VendorUpdate,
)
from app.services.vendor.vendor_service import VendorService


vendor_router = APIRouter(
    prefix="/vendors",
    tags=["Vendor Management"],
)


# ==========================================================
# CREATE VENDOR
# ==========================================================

@vendor_router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vendor(
    request: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:create")
    ),
):
    vendor = VendorService.create_vendor(
        db=db,
        current_user=current_user,
        request=request,
    )

    return vendor


# ==========================================================
# LIST VENDORS
# ==========================================================

@vendor_router.get(
    "",
    response_model=List[VendorResponse],  # Return list of VendorResponse
    status_code=status.HTTP_200_OK,
)
def list_vendors(
    status_filter: Optional[VendorStatus] = Query(
        default=None,
        alias="status",
        description="Filter vendors by status",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by vendor code, name, email, or tax ID",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:read")
    ),
):
    result = VendorService.list_vendors(
        db=db,
        status_filter=status_filter,
        search=search,
        skip=skip,
        limit=limit,
    )
    
    # Return only the vendors list
    return result.get("vendors", [])


# ==========================================================
# GET VENDOR BY ID
# ==========================================================

@vendor_router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def get_vendor_by_id(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:read")
    ),
):
    vendor = VendorService.get_vendor_by_id(
        db=db,
        vendor_id=vendor_id,
    )

    return vendor


# ==========================================================
# GET VENDOR BY CODE
# ==========================================================

@vendor_router.get(
    "/code/{vendor_code}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def get_vendor_by_code(
    vendor_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:read")
    ),
):
    vendor = VendorService.get_vendor_by_code(
        db=db,
        vendor_code=vendor_code,
    )

    return vendor


# ==========================================================
# UPDATE VENDOR
# ==========================================================

@vendor_router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def update_vendor(
    vendor_id: int,
    request: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:update")
    ),
):
    vendor = VendorService.update_vendor(
        db=db,
        current_user=current_user,
        vendor_id=vendor_id,
        request=request,
    )

    return vendor


# ==========================================================
# UPDATE VENDOR STATUS
# ==========================================================

@vendor_router.patch(
    "/{vendor_id}/status",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def update_vendor_status(
    vendor_id: int,
    request: VendorStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("vendor:update")
    ),
):
    vendor = VendorService.update_vendor_status(
        db=db,
        current_user=current_user,
        vendor_id=vendor_id,
        request=request,
    )

    return vendor