from fastapi import HTTPException, status

from app.models.identity.user import User
from app.services.authorization_service import AuthorizationService


def ensure_resource_access(
    user: User,
    resource_owner_id: int,
) -> None:
    allowed = AuthorizationService.can_access_resource(
        user=user,
        resource_owner_id=resource_owner_id,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource",
        )