from fastapi import HTTPException, status
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.models.approval.approval import (
    Approval,
    ApprovalStatus,
)
from app.models.approval.approval_step import (
    ApprovalStep,
    ApprovalStepStatus,
)

from app.models.identity.user import User



class ApprovalService:

    @staticmethod
    def create_approval(
        db: Session,
        purchase_request_id: int,
        policy_decisions: list[dict[str, Any]],
    ) -> Approval:

        if not policy_decisions:
            raise ValueError(
                "Cannot create approval without policy decisions"
            )

        approval = Approval(
            purchase_request_id=purchase_request_id,
            status=ApprovalStatus.PENDING.value,
            approval_type="ALL_REQUIRED",
        )

        db.add(approval)
        db.flush()

        step_count = 0

        for decision in policy_decisions:

            action = decision.get("action", {})

            if (
                action.get("type")
                != "REQUIRE_APPROVAL"
            ):
                continue

            required_role = action.get("role")

            if not required_role:
                continue

            step_count += 1

            step = ApprovalStep(
                approval_id=approval.id,
                required_role=required_role,
                sequence=step_count,
                status=ApprovalStepStatus.PENDING.value,
            )

            db.add(step)

        if step_count == 0:
            raise ValueError(
                "Policy decisions did not produce "
                "any approval steps"
            )

        db.flush()

        return approval



    @staticmethod
    def get_pending_approvals(
        db: Session,
        current_user: User,
    ) -> list[ApprovalStep]:

        # User has no role
        if (
            current_user.role is None
            or current_user.role.name is None
        ):
            return []

        approval_steps = db.query(ApprovalStep).join(
                Approval,
                Approval.id == ApprovalStep.approval_id,
            ).options(
                joinedload(
                    ApprovalStep.approval
                ).joinedload(
                    Approval.purchase_request
                )
            ).filter(
                # Only steps assigned to current role
                ApprovalStep.required_role == current_user.role.name,

                # Step must still be pending
                ApprovalStep.status == ApprovalStepStatus.PENDING.value,

                # Parent approval must still be active
                Approval.status == ApprovalStatus.PENDING.value,
            ).order_by(
                ApprovalStep.approval_id.asc(),
                ApprovalStep.sequence.asc(),
            ).all()

        actionable_steps = []

        for step in approval_steps:
            # Check whether any previous step
            # is still not approved
            previous_unapproved_step = db.query(ApprovalStep).filter(
                    ApprovalStep.approval_id == step.approval_id,
                    ApprovalStep.sequence < step.sequence,
                    ApprovalStep.status != ApprovalStepStatus.APPROVED.value,
                ).first()

            # If previous step exists and is not approved,
            # current step is not actionable yet
            if previous_unapproved_step is not None:
                continue

            actionable_steps.append(step)

        return actionable_steps


    @staticmethod
    def get_approval_by_id(
        db:Session,
        approval_id:int,
    ) -> Approval:

        approval = db.query(Approval).options(
            joinedload(Approval.steps)
        ).filter(
            Approval.id==approval_id
        ).first()

        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        return approval



    @staticmethod
    def cancel_previous_approvals(
        db: Session,
        purchase_request_id: int,
    ) -> list[Approval]:

        approvals = db.query(Approval).options(
                joinedload(Approval.steps)
            ).filter(
                Approval.purchase_request_id == purchase_request_id,
                Approval.status.in_([
                    ApprovalStatus.PENDING.value,
                    ApprovalStatus.CHANGES_REQUESTED.value,
                ]),
            ).all()
        

        for approval in approvals:
            # Close the approval cycle
            approval.status = ApprovalStatus.CANCELLED.value

            # Close pending approval steps
            for step in approval.steps:
                if step.status == ApprovalStepStatus.PENDING.value:
                    step.status = ApprovalStepStatus.SKIPPED.value

        db.flush()

        return approvals