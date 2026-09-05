from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Dict, Any

from app.models.procurement.purchase_request import PurchaseRequest


class ProcurementMCPService:
    """MCP service for procurement operations."""
    
    @staticmethod
    def get_procurement_requests(db: Session, limit: int = 10) -> Dict[str, Any]:
        """Get procurement requests."""
        try:
            requests = db.query(PurchaseRequest).options(
                joinedload(PurchaseRequest.items)
            ).order_by(desc(PurchaseRequest.created_at)).limit(limit).all()
            
            return {
                "found": True,
                "requests": [
                    {
                        "id": req.id,
                        "request_number": req.request_number,
                        "title": req.title,
                        "description": req.description,
                        "status": req.status,
                        "estimated_amount": float(req.estimated_amount) if req.estimated_amount else 0,
                        "currency": req.currency,
                        "created_at": req.created_at.isoformat() if req.created_at else None,
                        "items": [
                            {
                                "id": item.id,
                                "item_name": item.item_name,
                                "quantity": float(item.quantity) if item.quantity else 0,
                                "unit": item.unit,
                                "estimated_unit_price": float(item.estimated_unit_price) if item.estimated_unit_price else 0,
                                "total_price": float(item.total_price) if item.total_price else 0,
                            }
                            for item in req.items
                        ] if req.items else [],
                    }
                    for req in requests
                ],
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_pr_details(db: Session, pr_id: int) -> Dict[str, Any]:
        """Get details of a specific procurement request."""
        try:
            pr = db.query(PurchaseRequest).options(
                joinedload(PurchaseRequest.items)
            ).filter(PurchaseRequest.id == pr_id).first()
            
            if not pr:
                return {
                    "found": False,
                    "message": f"Procurement request with ID {pr_id} not found",
                }
            
            return {
                "found": True,
                "purchase_request": {
                    "id": pr.id,
                    "request_number": pr.request_number,
                    "title": pr.title,
                    "description": pr.description,
                    "requester_id": pr.requester_id,
                    "department_id": pr.department_id,
                    "estimated_amount": float(pr.estimated_amount) if pr.estimated_amount else 0,
                    "currency": pr.currency,
                    "status": pr.status,
                    "required_by_date": pr.required_by_date.isoformat() if pr.required_by_date else None,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "items": [
                        {
                            "id": item.id,
                            "item_name": item.item_name,
                            "description": item.description,
                            "quantity": float(item.quantity) if item.quantity else 0,
                            "unit": item.unit,
                            "estimated_unit_price": float(item.estimated_unit_price) if item.estimated_unit_price else 0,
                            "total_price": float(item.total_price) if item.total_price else 0,
                        }
                        for item in pr.items
                    ] if pr.items else [],
                },
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }