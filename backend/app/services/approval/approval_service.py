from typing import Any

from sqlalchemy.orm import Session

from app.models.approval.approval import (
    Approval,
    ApprovalStatus,
)
from app.models.approval.approval_step import (
    ApprovalStep,
    ApprovalStepStatus,
)


class ApprovalService:

    @staticmethod
    def create_approval(
        db:Session,
        purchase_request_id: int,
        policy_decisions: list[dict[str, Any]],
    ) -> Approval:

        if not policy_decisions:
            raise ValueError("Cannot create approval without policy decisions")

        approval = Approval(
            purchase_request_id=purchase_request_id,
            status=ApprovalStatus.PENDING.value,
            approval_type="ALL_REQUIRED"
        )

        db.add(approval)
        db.flush()

        step_count = 0

        for sequence, decision in enumerate(
            policy_decisions,
            1
        ):
            action = decision.get("action", {})

            if action.get("type") != "REQUIRE_APPROVAL":
                continue

            required_role = action.get("role")

            if not required_role:
                continue

            step = ApprovalStep(
                approval_id=approval.id,
                required_role=required_role,
                sequence=sequence,
                status=ApprovalStepStatus.PENDING.value,
            )

            db.add(step)
            step_count+=1

        if step_count == 0:
            raise ValueError(
                "Policy decisions did not produce "
                "any approval steps"
            )
        
        db.flush()

        return approval