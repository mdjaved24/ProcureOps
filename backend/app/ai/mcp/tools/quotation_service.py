from asyncio.log import logger

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Dict, Any

from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.quotation.quotation_item import QuotationItem
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation_requests.rfq_vendor import RFQVendor
from app.models.vendor.vendor import Vendor
from app.services.quotation.quotation_comparison_service import QuotationComparisonService


class QuotationMCPService:
    """MCP service for quotation operations."""
    
    @staticmethod
    def get_quotations(db: Session) -> Dict[str, Any]:
        """Get all quotations with vendor information."""
        try:
            quotations = db.query(Quotation).order_by(desc(Quotation.created_at)).all()
            
            result = []
            for q in quotations:
                rfq_vendor = db.query(RFQVendor).filter(RFQVendor.id == q.rfq_vendor_id).first()
                vendor_name = None
                vendor_id = None
                
                if rfq_vendor:
                    vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()
                    if vendor:
                        vendor_name = vendor.name
                        vendor_id = vendor.id
                
                result.append({
                    "id": q.id,
                    "quotation_number": q.quotation_number,
                    "vendor_name": vendor_name,
                    "vendor_id": vendor_id,
                    "total_amount": float(q.total_amount) if q.total_amount else 0,
                    "currency": q.currency,
                    "status": q.status,
                    "submitted_at": q.submitted_at.isoformat() if q.submitted_at else None,
                })
            
            return {
                "found": True,
                "quotations": result,
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_rfq_quotations(db: Session, rfq_number: str) -> Dict[str, Any]:
        """Get quotations for a specific RFQ."""
        try:
            rfq = db.query(RFQ).filter(RFQ.rfq_number == rfq_number).first()
            
            if not rfq:
                return {
                    "found": False,
                    "message": f"RFQ {rfq_number} not found",
                    "quotation_count": 0,
                    "quotations": [],
                }
            
            rfq_vendors = db.query(RFQVendor).filter(RFQVendor.rfq_id == rfq.id).all()
            quotations = []
            
            for rfq_vendor in rfq_vendors:
                quotation = db.query(Quotation).filter(
                    Quotation.rfq_vendor_id == rfq_vendor.id,
                    Quotation.status == QuotationStatus.SUBMITTED.value
                ).first()
                
                if not quotation:
                    continue
                
                items = db.query(QuotationItem).filter(
                    QuotationItem.quotation_id == quotation.id
                ).all()
                
                vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()
                
                quotations.append({
                    "quotation_number": quotation.quotation_number,
                    "vendor_id": rfq_vendor.vendor_id,
                    "vendor_name": vendor.name if vendor else None,
                    "status": quotation.status,
                    "currency": quotation.currency,
                    "subtotal": float(quotation.subtotal) if quotation.subtotal else 0,
                    "tax_amount": float(quotation.tax_amount) if quotation.tax_amount else 0,
                    "total_amount": float(quotation.total_amount) if quotation.total_amount else 0,
                    "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
                    "submitted_at": quotation.submitted_at.isoformat() if quotation.submitted_at else None,
                    "items": [
                        {
                            "item_name": item.item_name,
                            "description": item.description,
                            "quantity": float(item.quantity) if item.quantity else 0,
                            "unit": item.unit,
                            "unit_price": float(item.unit_price) if item.unit_price else 0,
                            "total_price": float(item.total_price) if item.total_price else 0,
                        }
                        for item in items
                    ] if items else [],
                })
            
            return {
                "found": True,
                "rfq_number": rfq.rfq_number,
                "rfq_title": rfq.title,
                "rfq_status": rfq.status,
                "quotation_count": len(quotations),
                "quotations": quotations,
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_quotation_details(db: Session, quotation_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific quotation."""
        try:
            quotation = db.query(Quotation).options(
                joinedload(Quotation.items)
            ).filter(Quotation.id == quotation_id).first()
            
            if not quotation:
                return {
                    "found": False,
                    "message": f"Quotation with ID {quotation_id} not found",
                }
            
            rfq_vendor = db.query(RFQVendor).filter(RFQVendor.id == quotation.rfq_vendor_id).first()
            vendor_name = None
            if rfq_vendor:
                vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()
                if vendor:
                    vendor_name = vendor.name
            
            return {
                "found": True,
                "quotation": {
                    "id": quotation.id,
                    "quotation_number": quotation.quotation_number,
                    "rfq_vendor_id": quotation.rfq_vendor_id,
                    "vendor_name": vendor_name,
                    "status": quotation.status,
                    "currency": quotation.currency,
                    "subtotal": float(quotation.subtotal) if quotation.subtotal else 0,
                    "tax_amount": float(quotation.tax_amount) if quotation.tax_amount else 0,
                    "total_amount": float(quotation.total_amount) if quotation.total_amount else 0,
                    "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
                    "notes": quotation.notes,
                    "submitted_at": quotation.submitted_at.isoformat() if quotation.submitted_at else None,
                    "items": [
                        {
                            "id": item.id,
                            "item_name": item.item_name,
                            "description": item.description,
                            "quantity": float(item.quantity) if item.quantity else 0,
                            "unit": item.unit,
                            "unit_price": float(item.unit_price) if item.unit_price else 0,
                            "total_price": float(item.total_price) if item.total_price else 0,
                        }
                        for item in quotation.items
                    ] if quotation.items else [],
                },
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def compare_rfq_quotations(db: Session, rfq_number: str) -> Dict[str, Any]:
        """Compare quotations for a closed RFQ."""
        try:
            rfq = db.query(RFQ).filter(RFQ.rfq_number == rfq_number).first()
            
            if not rfq:
                return {
                    "found": False,
                    "message": f"RFQ {rfq_number} not found",
                }
            
            # Check if RFQ is closed
            if rfq.status != RFQStatus.CLOSED.value:
                return {
                    "found": False,
                    "message": f"RFQ {rfq_number} is not closed. Quotations can only be compared after the RFQ is closed.",
                    "rfq_status": rfq.status,
                }
            
            comparison = QuotationComparisonService.compare_rfq_quotations(db, rfq.id)
            
            # Convert to dict with proper structure
            return {
                "found": True,
                "rfq_number": rfq.rfq_number,
                "title": rfq.title,
                "status": rfq.status,
                "quotation_count": len(comparison.quotations) if comparison.quotations else 0,
                "quotations": [
                    {
                        "rank": q.rank,
                        "quotation_id": q.quotation_id,
                        "vendor_id": q.vendor_id,
                        "vendor_name": q.vendor_name,
                        "vendor_code": q.vendor_code,
                        "total_amount": float(q.total_amount) if q.total_amount else 0,
                        "currency": q.currency,
                        "validity_date": q.validity_date.isoformat() if q.validity_date else None,
                    }
                    for q in comparison.quotations
                ] if comparison.quotations else [],
                "item_comparison": [
                    {
                        "rfq_item_id": item.rfq_item_id,
                        "item_name": item.item_name,
                        "description": item.description,
                        "quantity": float(item.quantity) if item.quantity else 0,
                        "unit": item.unit,
                        "prices": [
                            {
                                "quotation_id": p.quotation_id,
                                "vendor_id": p.vendor_id,
                                "vendor_name": p.vendor_name,
                                "quantity": float(p.quantity) if p.quantity else 0,
                                "unit_price": float(p.unit_price) if p.unit_price else 0,
                                "total_price": float(p.total_price) if p.total_price else 0,
                            }
                            for p in item.prices
                        ]
                    }
                    for item in comparison.item_comparison
                ] if comparison.item_comparison else [],
            }
        except Exception as e:
            logger.error(f"Error comparing quotations: {e}")
            return {
                "found": False,
                "error": str(e),
            }