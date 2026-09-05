from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.authorization import require_permission
from app.models.identity.user import User
from app.schemas.dashboard.dashboard_schema import DashboardSummaryResponse
from app.services.dashboard.dashboard_service import DashboardService


dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@dashboard_router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive dashboard summary including statistics and recent activity.
    Accessible to all authenticated users with role-based data filtering.
    """
    return DashboardService.get_dashboard_summary(db, current_user)


@dashboard_router.get(
    "/stats",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get dashboard statistics only.
    Accessible to all authenticated users with role-based data filtering.
    """
    return DashboardService.get_dashboard_stats(db, current_user)


@dashboard_router.get(
    "/recent-activity",
    response_model=list,
    status_code=status.HTTP_200_OK,
)
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get recent activity across all modules.
    Accessible to all authenticated users with role-based data filtering.
    """
    return DashboardService.get_recent_activity(db, current_user, limit)