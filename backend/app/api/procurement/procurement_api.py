from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.authorization import require_permission, require_any_permission
from app.core.dependencies import get_current_user, get_db
from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequest, PurchaseRequestStatus
from app.schemas.procurement.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestResponse,
    PurchaseRequestResubmitUpdate,
)
from app.services.procurement.procurement_service import ProcurementService

from app.services.authorization_service import (
    AuthorizationService,
)
from app.services.procurement.purchase_request_resubmission_service import PurchaseRequestResubmissionService
from app.services.procurement.purchase_request_workflow import transition_purchase_request

# Setup logger
logger = logging.getLogger(__name__)


procurement_router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"],
)


@procurement_router.post(
    "/requests",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_permission("procurement:create")
        )
    ],
)
def create_purchase_request(
    request: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new purchase request.
    Only users with 'procurement:create' permission can create requests.
    """
    if current_user.department_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a department",
        )

    try:
        return ProcurementService.create_purchase_request(
            db=db,
            data=request,
            current_user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@procurement_router.get(
    "/requests/{request_id}",
    response_model=PurchaseRequestResponse,
    dependencies=[
        Depends(
            require_permission("procurement:read")
        )
    ],
)
def get_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific purchase request by ID.
    Users can only access requests they own, unless they are ADMIN or AUDITOR.
    """
    purchase_request = ProcurementService.get_purchase_request(db=db, request_id=request_id)

    if purchase_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found"
        )

    if not AuthorizationService.can_access_resource(
        user=current_user,
        resource_owner_id=purchase_request.requester_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this purchase request",
        )

    return purchase_request


@procurement_router.get(
    "/requests",
    response_model=list[PurchaseRequestResponse],
    dependencies=[
        Depends(
            require_permission("procurement:read")
        )
    ],
)
def list_purchase_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List purchase requests based on user role:
    - EMPLOYEE: Only sees their own requests
    - All other roles see all requests
    """
    user_role = current_user.role.name.upper()
    
    # Roles that can see ALL purchase requests
    see_all_roles = [
        "ADMIN",
        "AUDITOR",
        "PROCUREMENT_MANAGER",
        "PROCUREMENT_HEAD",
        "FINANCE_OFFICER",
        "CFO",
        "LEGAL_OFFICER",
        "SECURITY_OFFICER",
        "COMPLIANCE_OFFICER",
        "PROCUREMENT_ANALYST"
    ]
    
    if user_role in see_all_roles:
        return db.query(PurchaseRequest).order_by(
            PurchaseRequest.created_at.desc()
        ).all()
    
    # Default: only show user's own requests
    return db.query(PurchaseRequest).filter(
        PurchaseRequest.requester_id == current_user.id
    ).order_by(PurchaseRequest.created_at.desc()).all()


@procurement_router.post(
    "/requests/{request_id}/submit",
    response_model=PurchaseRequestResponse,
    dependencies=[
        Depends(
            require_permission("procurement:submit")
        )
    ]
)
def submit_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a purchase request for review.
    Only the request owner can submit their own request.
    """
    purchase_request = ProcurementService.get_purchase_request(db=db, request_id=request_id)

    if not purchase_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found",
        )

    if not AuthorizationService.is_resource_owner(
        user=current_user,
        resource_owner_id=purchase_request.requester_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the request owner can submit this request",
        )

    transition_purchase_request(
        purchase_request,
        PurchaseRequestStatus.SUBMITTED,
    )

    db.commit()
    db.refresh(purchase_request)

    return purchase_request


@procurement_router.post(
    "/requests/{request_id}/start-review",
    response_model=PurchaseRequestResponse,
    dependencies=[
        Depends(
            require_any_permission([
                "procurement:review",
                "workflow:execute"
            ])
        )
    ]
)
def start_purchase_request_review(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start the review process for a purchase request.
    Users need 'procurement:review' or 'workflow:execute' permission.
    """
    purchase_request = ProcurementService.get_purchase_request(db=db, request_id=request_id)

    if not purchase_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found",
        )

    # Validate status transition
    if purchase_request.status != PurchaseRequestStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start review for request with status: {purchase_request.status}",
        )

    transition_purchase_request(
        purchase_request,
        PurchaseRequestStatus.UNDER_REVIEW,
    )

    db.commit()
    db.refresh(purchase_request)

    return purchase_request


@procurement_router.post(
    "/requests/{request_id}/evaluate",
    response_model=PurchaseRequestResponse,
    dependencies=[
        Depends(
            require_any_permission([
                "procurement:review",
                "workflow:execute",
                "workflow:resume"
            ])
        )
    ],
)
def evaluate_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate a purchase request and create approval workflow.
    Users need 'procurement:review', 'workflow:execute', or 'workflow:resume' permission.
    """
    try:
        purchase_request = (
            ProcurementService.get_purchase_request(
                db=db,
                request_id=request_id,
            )
        )

        if purchase_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found",
            )

        # Validate status
        if purchase_request.status != PurchaseRequestStatus.UNDER_REVIEW.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot evaluate request with status: {purchase_request.status}. Must be UNDER_REVIEW.",
            )

        try:
            ProcurementService.evaluate_and_create_approval(
                db=db,
                purchase_request=purchase_request,
            )

            db.commit()
            db.refresh(purchase_request)

            return purchase_request

        except ValueError as exc:
            db.rollback()
            logger.error(f"ValueError in evaluate: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            )

        except Exception as exc:
            db.rollback()
            logger.error(f"Unexpected error in evaluate: {str(exc)}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to evaluate purchase request: {str(exc)}",
            )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in evaluate_purchase_request: {str(exc)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate purchase request: {str(exc)}",
        )


@procurement_router.put(
    "/{purchase_request_id}/requested-changes",
)
def update_requested_changes(
    purchase_request_id: int,
    request: PurchaseRequestResubmitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_any_permission([
            "purchase_request:update",
            "procurement:update"
        ])
    ),
):
    """
    Update a purchase request with requested changes.
    Users need 'purchase_request:update' or 'procurement:update' permission.
    """
    purchase_request = (
        PurchaseRequestResubmissionService
        .update_requested_changes(
            db=db,
            purchase_request_id=purchase_request_id,
            current_user=current_user,
            request=request,
        )
    )

    try:
        db.commit()
        db.refresh(purchase_request)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Purchase request updated successfully",
        "purchase_request": {
            "id": purchase_request.id,
            "request_number": (
                purchase_request.request_number
            ),
            "status": purchase_request.status,
        },
    }


@procurement_router.post(
    "/{purchase_request_id}/resubmit",
    status_code=status.HTTP_200_OK,
)
def resubmit_purchase_request(
    purchase_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_any_permission([
            "purchase_request:update",
            "procurement:update",
            "workflow:resume"
        ])
    ),
):
    """
    Resubmit a purchase request after changes.
    Users need 'purchase_request:update', 'procurement:update', or 'workflow:resume' permission.
    """
    purchase_request = (
        PurchaseRequestResubmissionService
        .resubmit(
            db=db,
            purchase_request_id=purchase_request_id,
            current_user=current_user,
        )
    )

    return {
        "message": (
            "Purchase request resubmitted successfully"
        ),
        "purchase_request": {
            "id": purchase_request.id,
            "request_number": (
                purchase_request.request_number
            ),
            "status": purchase_request.status,
            "policy_id": purchase_request.policy_id,
        },
    }