from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.dependencies import get_current_user, get_db

from app.models.identity.user import User

from app.schemas.approval.approval_schema import (
    ApprovalDecisionRequest,
    ApprovalResponse,
    PendingApprovalResponse,
)

from app.services.approval.approval_decision_service import (
    ApprovalDecisionService,
)

from app.services.approval.approval_service import (
    ApprovalService,
)


approval_router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ==========================================================
# Decide approval
# ==========================================================

@approval_router.post(
    "/steps/{approval_step_id}/decision",
    status_code=status.HTTP_200_OK,
)
def decide_approval(
    approval_step_id: int,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    approval = ApprovalDecisionService.decide(
        db=db,
        approval_step_id=approval_step_id,
        current_user=current_user,
        decision=request.decision,
        comments=request.comments,
    )

    return {
        "message": "Approval decision processed successfully",
        "approval": {
            "id": approval.id,
            "purchase_request_id": (
                approval.purchase_request_id
            ),
            "status": approval.status,
            "approval_type": approval.approval_type,
        },
    }


# ==========================================================
# Get my pending approvals
# ==========================================================

@approval_router.get(
    "/my-pending",
    response_model=list[PendingApprovalResponse],
)
def get_my_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("approval:read")
    ),
):

    approval_steps = ApprovalService.get_pending_approvals(
        db=db,
        current_user=current_user,
    )

    results = []

    for step in approval_steps:

        approval = step.approval
        purchase_request = approval.purchase_request

        results.append(
            PendingApprovalResponse(
                approval_id=approval.id,
                approval_status=approval.status,

                approval_step_id=step.id,
                sequence=step.sequence,
                required_role=step.required_role,
                step_status=step.status,

                purchase_request_id=purchase_request.id,
                request_number=purchase_request.request_number,
                title=purchase_request.title,
                estimated_amount=purchase_request.estimated_amount,
                currency=purchase_request.currency,
                purchase_request_status=purchase_request.status,

                created_at=approval.created_at,
            )
        )

    return results


# ==========================================================
# Get approval details
# ==========================================================

@approval_router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("approval:read")
    ),
):

    approval = ApprovalService.get_approval_by_id(
        db=db,
        approval_id=approval_id,
    )

    return approval