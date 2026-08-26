from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.identity.user import User
from app.schemas.approval.approval_decision import (
    ApprovalDecisionRequest,
)
from app.services.approval.approval_decision_service import (
    ApprovalDecisionService,
)


approval_router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


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