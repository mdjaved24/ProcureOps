from sqlalchemy.orm import Session
from typing import Optional, Tuple
import re

from app.models.identity.user import User
from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.quotation_requests.rfq_vendor import RFQVendor


class QuotationAuthorizationService:
    """Authorization service for quotation actions."""

    @staticmethod
    def get_quotation(
        db: Session,
        quotation_id: Optional[int] = None,
        quotation_number: Optional[str] = None,
    ) -> Optional[Quotation]:
        """
        Get a quotation by ID or number.
        Handles both numeric IDs and QT-XXXXX format.
        """
        # Try by ID first
        if quotation_id:
            quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
            if quotation:
                return quotation
        
        # Try by quotation number
        if quotation_number:
            # First try exact match
            quotation = db.query(Quotation).filter(
                Quotation.quotation_number == quotation_number
            ).first()
            if quotation:
                return quotation
            
            # Try extracting numeric ID from quotation number
            match = re.search(r'(\d+)', quotation_number)
            if match:
                qt_id = int(match.group(1))
                quotation = db.query(Quotation).filter(Quotation.id == qt_id).first()
                if quotation:
                    return quotation
        
        # Try to find by ID if quotation_id was provided but not found above
        if quotation_id:
            # One more try with ID
            quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
            if quotation:
                return quotation
        
        return None

    @staticmethod
    def validate_action(
        db: Session,
        user: User,
        quotation: Quotation,
        action: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a user can perform an action on a quotation.
        Returns (allowed, message).
        """
        # Check if quotation exists
        if not quotation:
            return False, "Quotation not found."

        # Check if quotation is submitted
        if quotation.status != QuotationStatus.SUBMITTED.value:
            return False, f"Only submitted quotations can be {action.lower().replace('_', ' ')}. Current status: {quotation.status}"

        # Check if user has required role for the action
        if action == "APPROVE_QUOTATION":
            required_roles = ["PROCUREMENT_MANAGER", "PROCUREMENT_HEAD", "CFO", "ADMIN"]
            if user.role.name.upper() not in required_roles:
                return False, f"User role '{user.role.name}' does not have permission to approve quotations. Required roles: {', '.join(required_roles)}"
        
        elif action == "REJECT_QUOTATION":
            required_roles = ["PROCUREMENT_MANAGER", "PROCUREMENT_HEAD", "FINANCE_OFFICER", "CFO", "ADMIN"]
            if user.role.name.upper() not in required_roles:
                return False, f"User role '{user.role.name}' does not have permission to reject quotations. Required roles: {', '.join(required_roles)}"

        # Check if quotation can be approved/rejected based on RFQ status
        rfq_vendor = db.query(RFQVendor).filter(
            RFQVendor.id == quotation.rfq_vendor_id
        ).first()
        
        if rfq_vendor:
            from app.models.quotation_requests.rfq import RFQStatus
            if rfq_vendor.rfq and rfq_vendor.rfq.status == RFQStatus.CLOSED.value:
                return False, "Cannot modify quotations for a closed RFQ."

        return True, None