from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Dict, Any, Optional

from app.models.vendor.vendor import Vendor, VendorStatus


class VendorMCPService:
    """MCP service for vendor operations."""
    
    @staticmethod
    def search_vendors(db: Session, search: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for vendors."""
        try:
            query = db.query(Vendor)
            
            if search:
                search_pattern = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Vendor.vendor_code.ilike(search_pattern),
                        Vendor.name.ilike(search_pattern),
                        Vendor.email.ilike(search_pattern),
                        Vendor.city.ilike(search_pattern),
                        Vendor.country.ilike(search_pattern),
                    )
                )
            
            vendors = query.order_by(desc(Vendor.id)).limit(limit).all()
            
            return {
                "found": True,
                "count": len(vendors),
                "vendors": [
                    {
                        "id": v.id,
                        "vendor_code": v.vendor_code,
                        "name": v.name,
                        "email": v.email,
                        "phone": v.phone,
                        "city": v.city,
                        "state": v.state,
                        "country": v.country,
                        "status": v.status,
                    }
                    for v in vendors
                ],
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }
    
    @staticmethod
    def get_vendor(db: Session, vendor_id: Optional[int] = None, vendor_code: Optional[str] = None) -> Dict[str, Any]:
        """Get vendor details by ID or code."""
        try:
            if vendor_id is None and vendor_code is None:
                return {
                    "found": False,
                    "message": "Either vendor_id or vendor_code is required.",
                }
            
            query = db.query(Vendor)
            
            if vendor_id is not None:
                vendor = query.filter(Vendor.id == vendor_id).first()
            else:
                vendor = query.filter(Vendor.vendor_code == vendor_code.upper().strip()).first()
            
            if not vendor:
                return {
                    "found": False,
                    "message": "Vendor not found.",
                }
            
            return {
                "found": True,
                "vendor": {
                    "id": vendor.id,
                    "vendor_code": vendor.vendor_code,
                    "name": vendor.name,
                    "description": vendor.description,
                    "email": vendor.email,
                    "phone": vendor.phone,
                    "address": vendor.address,
                    "city": vendor.city,
                    "state": vendor.state,
                    "country": vendor.country,
                    "postal_code": vendor.postal_code,
                    "tax_id": vendor.tax_id,
                    "status": vendor.status,
                    "created_at": vendor.created_at.isoformat() if vendor.created_at else None,
                    "updated_at": vendor.updated_at.isoformat() if vendor.updated_at else None,
                },
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
            }