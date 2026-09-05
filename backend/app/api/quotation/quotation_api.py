from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.models.identity.user import User

from app.schemas.quotation.quotation_schema import (
    QuotationResponse,
    QuotationListResponse,
)

from app.schemas.quotation.quotation_comparison_schema import (
    RFQQuotationComparisonResponse,
)

from app.services.quotation.quotation_service import (
    QuotationService,
)

from app.services.quotation.quotation_comparison_service import (
    QuotationComparisonService,
)

from app.core.dependencies import get_current_user


quotation_router = APIRouter(
    prefix="/quotations",
    tags=["Quotations"],
)


# ==========================================================
# LIST QUOTATIONS
# ==========================================================

@quotation_router.get(
    "",
    response_model=list[QuotationListResponse],
)
def list_quotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuotationService.list_all_quotations(
        db=db,
    )


# ==========================================================
# GET QUOTATION BY ID
# ==========================================================

@quotation_router.get(
    "/{quotation_id}",
    response_model=QuotationResponse,
)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuotationService.get_quotation_by_id(
        db=db,
        quotation_id=quotation_id,
    )


# ==========================================================
# LIST QUOTATIONS FOR RFQ
# ==========================================================

@quotation_router.get(
    "/rfq/{rfq_id}",
    response_model=list[QuotationListResponse],
)
def list_quotations_for_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuotationService.list_quotations_for_rfq(
        db=db,
        rfq_id=rfq_id,
    )


# ==========================================================
# COMPARE RFQ QUOTATIONS
# ==========================================================

@quotation_router.get(
    "/rfq/{rfq_id}/compare",
    response_model=RFQQuotationComparisonResponse,
)
def compare_quotations(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuotationComparisonService.compare_rfq_quotations(
        db=db,
        rfq_id=rfq_id,
    )


# ==========================================================
# WITHDRAW QUOTATION
# ==========================================================

@quotation_router.post(
    "/{quotation_id}/withdraw",
    response_model=QuotationResponse,
)
def withdraw_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuotationService.withdraw_quotation(
        db=db,
        quotation_id=quotation_id,
        current_user=current_user,
    )