from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_current_user
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
                detail=f"Insufficient permissions. Required: {permission_code}",
            )

        return current_user

    return permission_dependency


def require_any_permission(permission_codes: List[str]):
    """
    Check if user has ANY of the listed permissions.
    Useful for features that can be accessed by multiple roles.
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ):
        user_permissions = {
            permission.code
            for permission in current_user.role.permissions
        }

        # Check if user has any of the required permissions
        for code in permission_codes:
            if code in user_permissions:
                return current_user

        # If no permission found, raise 403
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required any of: {', '.join(permission_codes)}",
        )

    return permission_dependency


def require_all_permissions(permission_codes: List[str]):
    """
    Check if user has ALL of the listed permissions.
    Useful for features that require multiple permissions.
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ):
        user_permissions = {
            permission.code
            for permission in current_user.role.permissions
        }

        missing_permissions = [
            code for code in permission_codes
            if code not in user_permissions
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Missing: {', '.join(missing_permissions)}",
            )

        return current_user

    return permission_dependency