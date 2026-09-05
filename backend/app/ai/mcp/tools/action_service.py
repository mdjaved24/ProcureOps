from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.quotation_requests.rfq_vendor import RFQVendor, RFQVendorStatus


class ActionMCPService:
    """MCP service for actions (approve/reject)."""
    
    @staticmethod
    def approve_quotation(db: Session, quotation_id: int) -> Dict[str, Any]:
        """Approve a quotation."""
        try:
            quotation = db.query(Quotation).filter(
                Quotation.id == quotation_id
            ).with_for_update().first()
            
            if not quotation:
                return {
                    "success": False,
                    "message": "Quotation not found.",
                }
            
            if quotation.status != QuotationStatus.SUBMITTED.value:
                return {
                    "success": False,
                    "message": f"Only submitted quotations can be approved. Current status: {quotation.status}",
                    "quotation": {
                        "id": quotation.id,
                        "quotation_number": quotation.quotation_number,
                        "status": quotation.status,
                    },
                }
            
            previous_status = quotation.status
            quotation.status = QuotationStatus.ACCEPTED.value
            
            db.commit()
            db.refresh(quotation)
            
            return {
                "success": True,
                "message": "Quotation approved successfully.",
                "quotation": {
                    "id": quotation.id,
                    "quotation_number": quotation.quotation_number,
                    "previous_status": previous_status,
                    "status": quotation.status,
                    "total_amount": float(quotation.total_amount) if quotation.total_amount else 0,
                    "currency": quotation.currency,
                },
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error approving quotation: {str(e)}",
            }
    
    @staticmethod
    def reject_quotation(db: Session, quotation_id: int) -> Dict[str, Any]:
        """Reject a quotation."""
        try:
            quotation = db.query(Quotation).filter(
                Quotation.id == quotation_id
            ).with_for_update().first()
            
            if not quotation:
                return {
                    "success": False,
                    "message": "Quotation not found.",
                }
            
            if quotation.status != QuotationStatus.SUBMITTED.value:
                return {
                    "success": False,
                    "message": f"Only submitted quotations can be rejected. Current status: {quotation.status}",
                    "quotation": {
                        "id": quotation.id,
                        "quotation_number": quotation.quotation_number,
                        "status": quotation.status,
                    },
                }
            
            previous_status = quotation.status
            quotation.status = QuotationStatus.REJECTED.value
            
            db.commit()
            db.refresh(quotation)
            
            return {
                "success": True,
                "message": "Quotation rejected successfully.",
                "quotation": {
                    "id": quotation.id,
                    "quotation_number": quotation.quotation_number,
                    "previous_status": previous_status,
                    "status": quotation.status,
                    "total_amount": float(quotation.total_amount) if quotation.total_amount else 0,
                    "currency": quotation.currency,
                },
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error rejecting quotation: {str(e)}",
            }