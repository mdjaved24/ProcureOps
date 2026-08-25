from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.core.dependencies import get_current_user, get_db
from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequest, PurchaseRequestStatus
from app.schemas.procurement.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestResponse,
)
from app.services.procurement.procurement_service import ProcurementService

from app.services.authorization_service import (
    AuthorizationService,
)
from app.services.procurement.purchase_request_workflow import transition_purchase_request


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
    request_id:int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.name in ("ADMIN","AUDITOR"):
        return db.query(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()).all()

    return db.query(PurchaseRequest).filter(
        PurchaseRequest.requester_id==current_user.id
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
    request_id:int,
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    purchase_request = ProcurementService.get_purchase_request(db=db,request_id=request_id)

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
            require_permission("procurement:review")
        )
    ]
)
def start_purchase_request_review(
    request_id:int,
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    purchase_request = ProcurementService.get_purchase_request(db=db,request_id=request_id)

    if not purchase_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found",
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
            require_permission("procurement:review")
        )
    ],
)
def evaluate_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate purchase request",
        )



    