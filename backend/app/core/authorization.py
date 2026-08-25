from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.identity.user import User


def require_permission(permission_code: str):
    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ):
        user_permissions = {
            permission.code
            for permission in current_user.role.permissions
        }

        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return permission_dependency