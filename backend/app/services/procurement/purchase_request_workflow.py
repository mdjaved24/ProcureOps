from fastapi import HTTPException, status

from app.models.procurement.purchase_request import (
    PurchaseRequestStatus,
)


VALID_TRANSITIONS = {
    PurchaseRequestStatus.DRAFT: {
        PurchaseRequestStatus.SUBMITTED,
        PurchaseRequestStatus.CANCELLED,
    },
    PurchaseRequestStatus.SUBMITTED: {
        PurchaseRequestStatus.UNDER_REVIEW,
        PurchaseRequestStatus.CANCELLED,
    },
    PurchaseRequestStatus.UNDER_REVIEW: {
    PurchaseRequestStatus.APPROVAL_PENDING,
    PurchaseRequestStatus.REJECTED,
    PurchaseRequestStatus.CANCELLED,
    },
    PurchaseRequestStatus.APPROVAL_PENDING: {
        PurchaseRequestStatus.APPROVED,
        PurchaseRequestStatus.REJECTED,
        PurchaseRequestStatus.CHANGES_REQUESTED,
    },
    PurchaseRequestStatus.CHANGES_REQUESTED: {
    PurchaseRequestStatus.UNDER_REVIEW,
    PurchaseRequestStatus.CANCELLED,
    },  
    PurchaseRequestStatus.APPROVED: {
        PurchaseRequestStatus.COMPLETED,
    },
    PurchaseRequestStatus.REJECTED: set(),
    PurchaseRequestStatus.CANCELLED: set(),
    PurchaseRequestStatus.COMPLETED: set(),
}


def can_transition(
    current_status: PurchaseRequestStatus,
    target_status: PurchaseRequestStatus,
) -> bool:
    return target_status in VALID_TRANSITIONS.get(
        current_status,
        set(),
    )


def transition_purchase_request(
    purchase_request,
    target_status: PurchaseRequestStatus,
) -> None:
    current_status = PurchaseRequestStatus(
        purchase_request.status
    )

    if not can_transition(
        current_status,
        target_status
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid purchase request transition: "
                f"{current_status.value} → "
                f"{target_status.value}"
            ),
        )

    purchase_request.status = target_status.value

    