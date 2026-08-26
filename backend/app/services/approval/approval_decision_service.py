from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.approval.approval import (
    Approval,
    ApprovalStatus,
)
from app.models.approval.approval_step import (
    ApprovalStep,
    ApprovalStepStatus,
)
from app.models.identity.user import User
from app.models.procurement.purchase_request import (
    PurchaseRequestStatus,
)
from app.services.procurement.purchase_request_workflow import (
    transition_purchase_request
)

from app.schemas.approval.approval_decision import (
    ApprovalDecision,
)


class ApprovalDecisionService:

    @staticmethod
    def decide(
        db:Session,
        approval_step_id:int,
        current_user: User,
        decision: ApprovalDecision,
        comments: str | None,
    ) -> Approval:

        # ---------Lock the approval step-----------------
        approval_step = db.query(ApprovalStep).filter(
            ApprovalStep.id==approval_step_id,
        ).with_for_update().first()

        if approval_step is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Approval step not found'
            )

        #-------- Verify if approval step is still pending ------------
        if approval_step.status != ApprovalStepStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Approval step has already been decided"
                ),
            )

        # Verify Role Authorization
        if (
            current_user.role is None
            or current_user.role.name
            != approval_step.required_role
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "User is not authorized to decide "
                    "this approval step"
                ),
            )

        # Load approval
        approval = db.query(Approval).filter(
            Approval.id==approval_step.approval_id,
        ).with_for_update().first()

        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        # Load purchase request
        purchase_request = approval.purchase_request

        if purchase_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found",
            )

        # Process decision
        decision_time = datetime.now(timezone.utc)

        if decision == ApprovalDecision.APPROVE:
            approval_step.status = ApprovalStepStatus.APPROVED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time

        elif decision == ApprovalDecision.REJECT:
            approval_step.status = ApprovalStepStatus.REJECTED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time
            approval.status = ApprovalStatus.REJECTED.value
            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.REJECTED
            )

        elif decision == ApprovalDecision.REQUEST_CHANGES:
            approval_step.status = ApprovalStepStatus.REJECTED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time
            approval.status = ApprovalStatus.CHANGES_REQUESTED.value
            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.CHANGES_REQUESTED
            )


        # Recalculate all required approvals
        if decision == ApprovalDecision.APPROVE:
            db.flush()
            
            remaining_steps = (
                db.query(ApprovalStep)
                .filter(
                    ApprovalStep.approval_id== approval.id,
                    ApprovalStep.status== ApprovalStepStatus.PENDING.value,
                ).count()
            )

            rejected_steps = (
                db.query(ApprovalStep)
                .filter(
                    ApprovalStep.approval_id== approval.id,
                    ApprovalStep.status== ApprovalStepStatus.REJECTED.value,
                ).count()
            )

            if rejected_steps > 0:
                approval.status = (
                    ApprovalStatus.REJECTED.value
                )

                transition_purchase_request(
                    purchase_request,
                    PurchaseRequestStatus.REJECTED,
                )


            elif remaining_steps == 0:

                approval.status = (
                    ApprovalStatus.APPROVED.value
                )

                transition_purchase_request(
                    purchase_request,
                    PurchaseRequestStatus.APPROVED,
                )


        # Persist transaction
        try:
            db.commit()
            db.refresh(approval)

        except Exception:
            db.rollback()
            raise

        return approval

    






