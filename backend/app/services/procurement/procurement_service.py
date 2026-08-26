from decimal import Decimal

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



class ProcurementService:

    @staticmethod
    def create_purchase_request(
        db: Session,
        data: PurchaseRequestCreate,
        current_user: User,
    ) -> PurchaseRequest:

        calculated_total = Decimal("0")

        purchase_request = PurchaseRequest(
            request_number="TEMP",
            title=data.title,
            description=data.description,
            requester_id=current_user.id,
            department_id=current_user.department_id,
            estimated_amount=data.estimated_amount,
            currency=data.currency.upper(),
            status=PurchaseRequestStatus.DRAFT.value,
            required_by_date=data.required_by_date,
        )

        db.add(purchase_request)
        db.flush()

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
        if calculated_total != data.estimated_amount:
            raise ValueError(
                "Estimated amount must equal the sum of item totals"
            )

        purchase_request.request_number = (
            f"PR-{purchase_request.id:06d}"
        )

        db.commit()
        db.refresh(purchase_request)

        return purchase_request


    @staticmethod
    def get_purchase_request(
        db:Session,
        request_id:int
    )-> PurchaseRequest | None:
        purchase_request = db.query(PurchaseRequest).filter(PurchaseRequest.id==request_id).first()

        return purchase_request

    

    @staticmethod
    def evaluate_and_create_approval(
        db: Session,
        purchase_request: PurchaseRequest,
    ):
        current_status = PurchaseRequestStatus(
            purchase_request.status
        )

        if current_status != PurchaseRequestStatus.UNDER_REVIEW:
            raise ValueError(
                "Purchase request must be UNDER_REVIEW "
                "before policy evaluation"
            )

        context = {
            "estimated_amount": (
                purchase_request.estimated_amount
            ),
        }

        policy = PolicyResolver.resolve(
            db=db,
            context=context,
        )

        purchase_request.policy_id = policy["id"]

        decisions = PolicyEngine.evaluate_policy(
            policy=policy,
            context=context,
        )

        if not decisions:
            raise ValueError(
                "No applicable policy rules were triggered"
            )

        approval = ApprovalService.create_approval(
            db=db,
            purchase_request_id=purchase_request.id,
            policy_decisions=decisions,
        )

        transition_purchase_request(
            purchase_request,
            PurchaseRequestStatus.APPROVAL_PENDING,
        )

        return approval