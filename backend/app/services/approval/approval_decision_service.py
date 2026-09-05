from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.approval.approval import Approval, ApprovalStatus
from app.models.approval.approval_step import ApprovalStep, ApprovalStepStatus
from app.models.audit.audit_log import AuditActorType
from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequestStatus

from app.schemas.approval.approval_schema import ApprovalDecision

from app.services.audit.audit_service import AuditService
from app.services.procurement.purchase_request_workflow import transition_purchase_request


class ApprovalDecisionService:

    @staticmethod
    def decide(
        db: Session,
        approval_step_id: int,
        current_user: User,
        decision: ApprovalDecision,
        comments: str | None,
    ) -> Approval:

        approval_step = db.query(ApprovalStep).filter(
            ApprovalStep.id == approval_step_id
            ).with_for_update().first()

        if approval_step is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval step not found",
            )

        if approval_step.status != ApprovalStepStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Approval step has already been decided",
            )

        if (
            current_user.role is None or 
            current_user.role.name != approval_step.required_role
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to decide this approval step",
            )

        approval = db.query(Approval).filter(
            Approval.id == approval_step.approval_id
            ).with_for_update().first()
        

        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        previous_unapproved_step = db.query(ApprovalStep).filter(
                ApprovalStep.approval_id == approval.id,
                ApprovalStep.sequence < approval_step.sequence,
                ApprovalStep.status != ApprovalStepStatus.APPROVED.value,
            ).order_by(ApprovalStep.sequence.asc()).first()
        

        if previous_unapproved_step is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Previous approval step must be completed before this step can be decided",
            )

        purchase_request = approval.purchase_request

        if purchase_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found",
            )

        previous_step_state = {
            "status": approval_step.status,
            "decided_by": approval_step.decided_by,
            "decision_at": approval_step.decision_at.isoformat() if approval_step.decision_at else None,
            "decision_comments": approval_step.decision_comments,
        }

        previous_approval_state = {
            "status": approval.status,
        }

        previous_pr_state = {
            "status": purchase_request.status,
        }

        decision_time = datetime.now(timezone.utc)

        if decision == ApprovalDecision.APPROVE:

            approval_step.status = ApprovalStepStatus.APPROVED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time
            approval_step.decision_comments = comments

            audit_action = "APPROVAL_STEP_APPROVED"

        elif decision == ApprovalDecision.REJECT:

            approval_step.status = ApprovalStepStatus.REJECTED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time
            approval_step.decision_comments = comments

            approval.status = ApprovalStatus.REJECTED.value

            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.REJECTED,
            )

            audit_action = "APPROVAL_STEP_REJECTED"

        elif decision == ApprovalDecision.REQUEST_CHANGES:

            approval_step.status = ApprovalStepStatus.CHANGES_REQUESTED.value
            approval_step.decided_by = current_user.id
            approval_step.decision_at = decision_time
            approval_step.decision_comments = comments

            approval.status = ApprovalStatus.CHANGES_REQUESTED.value

            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.CHANGES_REQUESTED,
            )

            audit_action = "APPROVAL_STEP_CHANGES_REQUESTED"

        else:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval decision",
            )

        if decision == ApprovalDecision.APPROVE:

            db.flush()

            remaining_steps = db.query(ApprovalStep).filter(
                    ApprovalStep.approval_id == approval.id,
                    ApprovalStep.status == ApprovalStepStatus.PENDING.value,
                ).count()

            if remaining_steps == 0:

                approval.status = ApprovalStatus.APPROVED.value

                transition_purchase_request(
                    purchase_request,
                    PurchaseRequestStatus.APPROVED,
                )

        db.flush()

        AuditService.log(
            db=db,

            actor_type=AuditActorType.USER,
            actor_id=current_user.id,

            action=audit_action,

            resource_type="APPROVAL_STEP",
            resource_id=approval_step.id,

            previous_state=previous_step_state,

            new_state={
                "status": approval_step.status,
                "decided_by": approval_step.decided_by,
                "decision_at": approval_step.decision_at.isoformat() if approval_step.decision_at else None,
                "decision_comments": approval_step.decision_comments,
            },

            metadata={
                "approval_id": approval.id,
                "purchase_request_id": purchase_request.id,
                "required_role": approval_step.required_role,
                "comments": comments,
            },
        )

        if previous_approval_state["status"] != approval.status:

            AuditService.log(
                db=db,

                actor_type=AuditActorType.SYSTEM,
                actor_id=None,

                action="APPROVAL_STATUS_CHANGED",

                resource_type="APPROVAL",
                resource_id=approval.id,

                previous_state=previous_approval_state,

                new_state={
                    "status": approval.status,
                },

                metadata={
                    "purchase_request_id": purchase_request.id,
                },
            )

        if previous_pr_state["status"] != purchase_request.status:

            AuditService.log(
                db=db,

                actor_type=AuditActorType.SYSTEM,
                actor_id=None,

                action="PURCHASE_REQUEST_STATUS_CHANGED",

                resource_type="PURCHASE_REQUEST",
                resource_id=purchase_request.id,

                previous_state=previous_pr_state,

                new_state={
                    "status": purchase_request.status,
                },

                metadata={
                    "approval_id": approval.id,
                },
            )

        try:

            db.commit()
            db.refresh(approval)

        except Exception:

            db.rollback()
            raise

        return approval