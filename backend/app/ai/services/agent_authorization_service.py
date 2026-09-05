from sqlalchemy.orm import Session
from typing import Optional

from app.models.identity.user import User


class AgentAuthorizationService:
    """Authorization service for agent actions."""

    # Map agent actions to permission codes
    ACTION_PERMISSION_MAP = {
        "APPROVE_QUOTATION": "approval:approve",
        "REJECT_QUOTATION": "approval:reject",
        "GET_RFQS": "rfq:read",
        "GET_RFQ_DETAILS": "rfq:read",
        "GET_RFQ_STATUS": "rfq:read",
        "GET_QUOTATIONS": "quotation:read",
        "GET_RFQ_QUOTATIONS": "quotation:read",
        "GET_QUOTATION_DETAILS": "quotation:read",
        "COMPARE_QUOTATIONS": "quotation:read",
        "SEARCH_VENDORS": "vendor:read",
        "GET_VENDOR": "vendor:read",
        "GET_VENDOR_DETAILS": "vendor:read",
        "GET_PROCUREMENT_REQUESTS": "procurement:read",
        "GET_PROCUREMENT_REQUEST_DETAILS": "procurement:read",
        "GET_APPROVALS": "approval:read",
    }

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def has_permission(user: User, action: str) -> bool:
        """
        Check if the user has permission for an action.
        """
        permission_code = AgentAuthorizationService.ACTION_PERMISSION_MAP.get(action)
        
        if permission_code is None:
            # If no specific permission is defined, allow the action
            # This should be reviewed for security
            return True

        # Check if user has the required permission
        user_permissions = {permission.code for permission in user.role.permissions}
        return permission_code in user_permissions

    @staticmethod
    def is_action_authorized(
        db: Session,
        user_id: int,
        action: str,
    ) -> bool:
        """
        Check if a user is authorized for an action.
        """
        user = AgentAuthorizationService.get_user(db, user_id)

        if user is None:
            return False

        if not user.is_active:
            return False

        return AgentAuthorizationService.has_permission(user, action)