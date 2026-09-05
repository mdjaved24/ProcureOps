from fastapi import APIRouter, Depends

from app.core.authorization import require_permission
from app.models.identity.user import User


test_auth_router = APIRouter(
    prefix="/test-auth",
    tags=["Authorization"],
)


@test_auth_router.get(
    "/procurement-read",
    dependencies=[
        Depends(
            require_permission("procurement:read")
        )
    ],
)
def procurement_read_test():
    return {
        "message": "You have procurement:read permission"
    }


@test_auth_router.get(
    "/admin-users",
    dependencies=[
        Depends(
            require_permission("admin:users")
        )
    ],
)
def admin_users_test():
    return {
        "message": "You have admin:users permission"
    }