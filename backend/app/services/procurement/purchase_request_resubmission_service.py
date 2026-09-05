from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.approval.approval import Approval, ApprovalStatus
from app.models.approval.approval_step import ApprovalStep, ApprovalStepStatus
from app.models.audit.audit_log import AuditActorType
from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequest, PurchaseRequestStatus
from app.models.procurement.purchase_request_item import PurchaseRequestItem

from app.schemas.procurement.purchase_request import PurchaseRequestResubmitUpdate

from app.services.approval.approval_service import ApprovalService
from app.services.audit.audit_service import AuditService
from app.services.policy.policy_engine import PolicyEngine
from app.services.policy.policy_resolver import PolicyResolver
from app.services.procurement.purchase_request_workflow import transition_purchase_request


class PurchaseRequestResubmissionService:

    @staticmethod
    def update_requested_changes(
        db: Session,
        purchase_request_id: int,
        current_user: User,
        request: PurchaseRequestResubmitUpdate,
    ) -> PurchaseRequest:

        purchase_request = db.query(PurchaseRequest).filter(
            PurchaseRequest.id == purchase_request_id
            ).with_for_update().first()

        if purchase_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found",
            )

        if purchase_request.requester_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to modify this purchase request",
            )

        if purchase_request.status != PurchaseRequestStatus.CHANGES_REQUESTED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Purchase request can only be edited when changes have been requested",
            )

        purchase_request.title = request.title
        purchase_request.description = request.description
        purchase_request.department_id = request.department_id
        purchase_request.currency = request.currency.upper()
        purchase_request.required_by_date = request.required_by_date

        purchase_request.estimated_amount = sum(
            item.quantity * item.estimated_unit_price
            for item in request.items
        )

        purchase_request.items.clear()
        db.flush()

        for item_data in request.items:

            total_price = item_data.quantity * item_data.estimated_unit_price

            item = PurchaseRequestItem(
                purchase_request_id=purchase_request.id,
                item_name=item_data.item_name,
                description=item_data.description,
                quantity=item_data.quantity,
                unit=item_data.unit,
                estimated_unit_price=item_data.estimated_unit_price,
                total_price=total_price,
            )

            db.add(item)

        db.flush()

        return purchase_request

    @staticmethod
    def resubmit(
        db: Session,
        purchase_request: PurchaseRequest,
        current_user: User,
    ) -> PurchaseRequest:

        if purchase_request.requester_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to resubmit this purchase request",
            )

        if purchase_request.status != PurchaseRequestStatus.CHANGES_REQUESTED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only purchase requests with requested changes can be resubmitted",
            )

        previous_pr_state = {
            "status": purchase_request.status,
            "policy_id": purchase_request.policy_id,
        }

        old_approval = (
            db.query(Approval)
            .filter(
                Approval.purchase_request_id == purchase_request.id,
                Approval.status == ApprovalStatus.CHANGES_REQUESTED.value,
            )
            .order_by(Approval.id.desc())
            .first()
        )

        if old_approval is not None:

            old_approval.status = ApprovalStatus.CANCELLED.value

            db.query(ApprovalStep).filter(
                ApprovalStep.approval_id == old_approval.id,
                ApprovalStep.status == ApprovalStepStatus.PENDING.value,
            ).update(
                {
                    ApprovalStep.status: ApprovalStepStatus.SKIPPED.value
                },
                synchronize_session=False,
            )

            db.flush()

        transition_purchase_request(
            purchase_request,
            PurchaseRequestStatus.SUBMITTED,
        )

        db.flush()

        context = {
            "estimated_amount": purchase_request.estimated_amount,
            "currency": purchase_request.currency,
            "department_id": purchase_request.department_id,
            "requester_id": purchase_request.requester_id,
        }

        policy_snapshot = PolicyResolver.resolve(
            db=db,
            context=context,
        )

        purchase_request.policy_id = policy_snapshot["id"]

        decisions = PolicyEngine.evaluate_policy(
            policy=policy_snapshot,
            context=context,
        )

        approval_required = any(
            decision.get("action", {}).get("type") == "REQUIRE_APPROVAL"
            for decision in decisions
        )

        if approval_required:

            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.UNDER_REVIEW,
            )

            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.APPROVAL_PENDING,
            )

            ApprovalService.create_approval(
                db=db,
                purchase_request_id=purchase_request.id,
                policy_decisions=decisions,
            )

        else:

            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.APPROVED,
            )

        AuditService.log(
            db=db,

            actor_type=AuditActorType.USER,
            actor_id=current_user.id,

            action="PURCHASE_REQUEST_RESUBMITTED",

            resource_type="PURCHASE_REQUEST",
            resource_id=purchase_request.id,

            previous_state=previous_pr_state,

            new_state={
                "status": purchase_request.status,
                "policy_id": purchase_request.policy_id,
            },

            metadata={
                "resubmission_type": "CHANGES_REQUESTED",
                "approval_required": approval_required,
                "old_approval_cancelled": old_approval is not None,
            },
        )

        db.commit()
        db.refresh(purchase_request)

        return purchase_request