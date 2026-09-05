from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Dict, Any

from app.models.approval.approval import Approval
from app.models.approval.approval_step import ApprovalStep


class ApprovalMCPService:
    """MCP service for approval operations."""
    
    @staticmethod
    def get_approvals(db: Session) -> Dict[str, Any]:
        """Get pending approvals."""
        try:
            approvals = db.query(Approval).options(
                joinedload(Approval.steps),
                joinedload(Approval.purchase_request)
            ).filter(
                Approval.status == "PENDING"
            ).order_by(desc(Approval.created_at)).all()
            
            result = []
            for approval in approvals:
                pr = approval.purchase_request
                for step in approval.steps:
                    if step.status == "PENDING":
                        result.append({
                            "id": approval.id,
                            "approval_step_id": step.id,
                            "request_number": pr.request_number if pr else None,
                            "title": pr.title if pr else None,
                            "estimated_amount": float(pr.estimated_amount) if pr and pr.estimated_amount else 0,
                            "currency": pr.currency if pr else "INR",
                            "required_role": step.required_role,
                            "status": step.status,
                            "created_at": approval.created_at.isoformat() if approval.created_at else None,
                        })
            
            return {
                "found": True,
                "approvals": result,
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }