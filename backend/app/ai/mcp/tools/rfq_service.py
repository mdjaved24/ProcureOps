from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Dict, Any

from app.models.quotation_requests.rfq import RFQ
from app.models.quotation_requests.rfq_item import RFQItem


class RFQMCPService:
    """MCP service for RFQ operations."""
    
    @staticmethod
    def get_rfqs(db: Session, limit: int = 10) -> Dict[str, Any]:
        """Get a list of RFQs."""
        try:
            rfqs = db.query(RFQ).options(
                joinedload(RFQ.items)
            ).order_by(desc(RFQ.created_at)).limit(limit).all()
            
            return {
                "found": True,
                "rfqs": [
                    {
                        "id": rfq.id,
                        "rfq_number": rfq.rfq_number,
                        "title": rfq.title,
                        "status": rfq.status,
                        "description": rfq.description,
                        "created_at": rfq.created_at.isoformat() if rfq.created_at else None,
                        "items": [
                            {
                                "id": item.id,
                                "item_name": item.item_name,
                                "quantity": float(item.quantity) if item.quantity else 0,
                                "unit": item.unit,
                            }
                            for item in rfq.items
                        ] if rfq.items else [],
                    }
                    for rfq in rfqs
                ],
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_rfq_details(db: Session, rfq_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific RFQ."""
        try:
            rfq = db.query(RFQ).options(
                joinedload(RFQ.items),
                joinedload(RFQ.vendors)
            ).filter(RFQ.id == rfq_id).first()
            
            if not rfq:
                return {
                    "found": False,
                    "message": f"RFQ with ID {rfq_id} not found",
                }
            
            return {
                "found": True,
                "rfq": {
                    "id": rfq.id,
                    "rfq_number": rfq.rfq_number,
                    "purchase_request_id": rfq.purchase_request_id,
                    "title": rfq.title,
                    "description": rfq.description,
                    "status": rfq.status,
                    "issue_date": rfq.issue_date.isoformat() if rfq.issue_date else None,
                    "submission_deadline": rfq.submission_deadline.isoformat() if rfq.submission_deadline else None,
                    "created_at": rfq.created_at.isoformat() if rfq.created_at else None,
                    "items": [
                        {
                            "id": item.id,
                            "item_name": item.item_name,
                            "description": item.description,
                            "quantity": float(item.quantity) if item.quantity else 0,
                            "unit": item.unit,
                        }
                        for item in rfq.items
                    ] if rfq.items else [],
                    "vendors": [
                        {
                            "id": vendor.id,
                            "vendor_id": vendor.vendor_id,
                            "status": vendor.status,
                            "invited_at": vendor.invited_at.isoformat() if vendor.invited_at else None,
                        }
                        for vendor in rfq.vendors
                    ] if rfq.vendors else [],
                },
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_rfq_status(db: Session, rfq_id: int) -> Dict[str, Any]:
        """Get the status of a specific RFQ."""
        try:
            rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
            
            if not rfq:
                return {
                    "found": False,
                    "message": f"RFQ with ID {rfq_id} not found",
                }
            
            return {
                "found": True,
                "rfq_number": rfq.rfq_number,
                "status": rfq.status,
                "title": rfq.title,
                "submission_deadline": rfq.submission_deadline.isoformat() if rfq.submission_deadline else None,
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }