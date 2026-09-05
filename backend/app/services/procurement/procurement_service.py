from decimal import Decimal
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.procurement.purchase_request import (
    PurchaseRequest,
    PurchaseRequestStatus,
)
from app.models.procurement.purchase_request_item import (
    PurchaseRequestItem,
)
from app.models.identity.user import User
from app.schemas.procurement.purchase_request import (
    PurchaseRequestCreate,
)

from app.models.procurement.purchase_request import (
    PurchaseRequestStatus,
)

from app.services.approval.approval_service import (
    ApprovalService,
)

from app.services.policy.policy_engine import (
    PolicyEngine,
)

from app.services.policy.policy_resolver import PolicyResolver
from app.services.procurement.purchase_request_workflow import (
    transition_purchase_request,
)

# Setup logger
logger = logging.getLogger(__name__)


class ProcurementService:

    @staticmethod
    def create_purchase_request(
        db: Session,
        data: PurchaseRequestCreate,
        current_user: User,
    ) -> PurchaseRequest:

        estimated_amount = sum(
            item.quantity * item.estimated_unit_price
            for item in data.items
        )

        purchase_request = PurchaseRequest(
            request_number="TEMP",
            title=data.title,
            description=data.description,
            requester_id=current_user.id,
            department_id=current_user.department_id,
            estimated_amount=estimated_amount,
            currency=data.currency.upper(),
            status=PurchaseRequestStatus.DRAFT.value,
            required_by_date=data.required_by_date,
        )

        db.add(purchase_request)
        db.flush()

        calculated_total = Decimal("0")

        for item_data in data.items:
            total_price = (
                item_data.quantity
                * item_data.estimated_unit_price
            )

            calculated_total += total_price

            item = PurchaseRequestItem(
                purchase_request_id=purchase_request.id,
                item_name=item_data.item_name,
                description=item_data.description,
                quantity=item_data.quantity,
                unit=item_data.unit,
                estimated_unit_price=(
                    item_data.estimated_unit_price
                ),
                total_price=total_price,
            )

            db.add(item)

        # Server-side financial consistency check.
        if calculated_total != estimated_amount:
            raise ValueError("Estimated amount must equal the sum of item totals")

        purchase_request.request_number = (
            f"PR-{purchase_request.id:06d}"
        )

        db.commit()
        db.refresh(purchase_request)

        return purchase_request

    @staticmethod
    def get_purchase_request(
        db: Session,
        request_id: int
    ) -> PurchaseRequest | None:
        purchase_request = db.query(PurchaseRequest).filter(
            PurchaseRequest.id == request_id
        ).first()
        return purchase_request

    @staticmethod
    def evaluate_and_create_approval(
        db: Session,
        purchase_request: PurchaseRequest,
    ):
        """
        Evaluate a purchase request and create approval workflow.
        """
        current_status = PurchaseRequestStatus(purchase_request.status)

        if current_status != PurchaseRequestStatus.UNDER_REVIEW:
            raise ValueError(
                "Purchase request must be UNDER_REVIEW "
                "before policy evaluation"
            )

        try:
            # Build context for policy evaluation
            context = {
                "estimated_amount": float(purchase_request.estimated_amount),
                "department_id": purchase_request.department_id,
                "requester_id": purchase_request.requester_id,
                "currency": purchase_request.currency,
                "request_id": purchase_request.id,
            }

            logger.info(f"Evaluating policy for purchase request {purchase_request.id}")
            logger.info(f"Context: {context}")

            # Resolve policy
            policy = PolicyResolver.resolve(
                db=db,
                context=context,
            )

            if not policy:
                logger.error(f"No policy found for purchase request {purchase_request.id}")
                raise ValueError("No applicable policy found for this request")

            logger.info(f"Policy resolved: {policy}")

            # Get policy ID
            policy_id = policy.get("id")
            if not policy_id:
                logger.error(f"Policy has no ID: {policy}")
                raise ValueError("Invalid policy configuration: missing ID")

            purchase_request.policy_id = policy_id

            # Evaluate policy
            decisions = PolicyEngine.evaluate_policy(
                policy=policy,
                context=context,
            )

            if not decisions:
                logger.warning(f"No policy decisions triggered for request {purchase_request.id}")
                raise ValueError(
                    "No applicable policy rules were triggered"
                )

            logger.info(f"Policy decisions: {decisions}")

            # Create approval workflow
            approval = ApprovalService.create_approval(
                db=db,
                purchase_request_id=purchase_request.id,
                policy_decisions=decisions,
            )

            logger.info(f"Approval created: {approval.id}")

            # Transition to approval pending
            transition_purchase_request(
                purchase_request,
                PurchaseRequestStatus.APPROVAL_PENDING,
            )

            return approval

        except ValueError as e:
            logger.error(f"ValueError in evaluate_and_create_approval: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in evaluate_and_create_approval: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise