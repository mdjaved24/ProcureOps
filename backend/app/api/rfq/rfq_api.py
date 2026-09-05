from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    status,
    Query
)
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.dependencies import (
    get_current_user,
    get_db,
)

from app.models.identity.user import User

from app.models.quotation_requests.rfq import RFQStatus

from app.schemas.quotation_requests.rfq_schema import (
    RFQCreate,
    RFQResponse,
    RFQUpdate,
    RFQVendorAdd,
)

from app.services.quotation.quotation_comparison_service import QuotationComparisonService
from app.schemas.quotation.quotation_comparison_schema import RFQQuotationComparisonResponse

from app.services.rfq.rfq_service import (
    RFQService,
)


rfq_router = APIRouter(
    prefix="/rfqs",
    tags=["RFQs"],
)


# ==========================================================
# CREATE RFQ
# ==========================================================

@rfq_router.post(
    "",
    response_model=RFQResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rfq(
    request: RFQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:create")
    ),
):
    rfq = RFQService.create_rfq(
        db=db,
        current_user=current_user,
        request=request,
    )

    return rfq


# ==========================================================
# GET RFQ BY ID
# ==========================================================

@rfq_router.get(
    "/{rfq_id}",
    response_model=RFQResponse,
)
def get_rfq_by_id(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:read")
    ),
):
    rfq = RFQService.get_rfq_by_id(
        db=db,
        rfq_id=rfq_id,
    )

    return rfq


# ==========================================================
# LIST RFQs
# ==========================================================

@rfq_router.get(
    "",
    response_model=list[RFQResponse],
)
def list_rfqs(
    status_filter: Optional[RFQStatus] = Query(
        default=None,
        description="Filter by RFQ status",
    ),
    purchase_request_id: Optional[int] = Query(
        default=None,
        description="Filter by purchase request ID",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:read")
    ),
):
    rfqs = RFQService.list_rfqs(
        db=db,
        status_filter=status_filter,
        purchase_request_id=purchase_request_id,
        skip=skip,
        limit=limit,
    )

    return rfqs


# ==========================================================
# UPDATE RFQ
# ==========================================================

@rfq_router.put(
    "/{rfq_id}",
    response_model=RFQResponse,
)
def update_rfq(
    rfq_id: int,
    request: RFQUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:update")
    ),
):
    rfq = RFQService.update_rfq(
        db=db,
        rfq_id=rfq_id,
        current_user=current_user,
        request=request,
    )

    return rfq


# ==========================================================
# ADD VENDOR TO RFQ
# ==========================================================

@rfq_router.post(
    "/{rfq_id}/vendors",
    response_model=RFQResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_vendor_to_rfq(
    rfq_id: int,
    request: RFQVendorAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:update")
    ),
):
    rfq = RFQService.add_vendor(
        db=db,
        rfq_id=rfq_id,
        vendor_id=request.vendor_id,
        current_user=current_user,
    )

    return rfq


# ==========================================================
# ISSUE RFQ
# ==========================================================

@rfq_router.post(
    "/{rfq_id}/issue",
    response_model=RFQResponse,
)
def issue_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:update")
    ),
):
    rfq = RFQService.issue_rfq(
        db=db,
        rfq_id=rfq_id,
        current_user=current_user,
    )

    return rfq


# ==========================================================
# CLOSE RFQ
# ==========================================================

@rfq_router.post(
    "/{rfq_id}/close",
    response_model=RFQResponse,
)
def close_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:update")
    ),
):
    rfq = RFQService.close_rfq(
        db=db,
        rfq_id=rfq_id,
        current_user=current_user,
    )

    return rfq


# ==========================================================
# CANCEL RFQ
# ==========================================================

@rfq_router.post(
    "/{rfq_id}/cancel",
    response_model=RFQResponse,
)
def cancel_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("rfq:update")
    ),
):
    rfq = RFQService.cancel_rfq(
        db=db,
        rfq_id=rfq_id,
        current_user=current_user,
    )

    return rfq




# ==========================================================
# COMPARE QUOTATIONS FOR RFQ
# ==========================================================

@rfq_router.get(
    "/{rfq_id}/quotations/comparison",
    response_model=(
        RFQQuotationComparisonResponse
    ),
)
def compare_rfq_quotations(
    rfq_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_permission(
            "rfq:read"
        )
    ),
):

    comparison = (
        QuotationComparisonService
        .compare_rfq_quotations(

            db=db,

            rfq_id=rfq_id,
        )
    )

    return comparison