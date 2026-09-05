from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.identity.user import User
from app.models.procurement.purchase_request import PurchaseRequest, PurchaseRequestStatus
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.vendor.vendor import Vendor, VendorStatus
from app.models.quotation_requests.rfq_vendor import RFQVendor


class DashboardService:
    """Service for dashboard statistics and data"""

    @staticmethod
    def get_dashboard_stats(
        db: Session,
        current_user: User
    ) -> dict:
        """
        Get comprehensive dashboard statistics based on user role
        """
        stats = {}

        # Base statistics - accessible to all authenticated users
        stats["total_vendors"] = DashboardService._get_total_vendors(db)
        stats["active_vendors"] = DashboardService._get_active_vendors(db)
        
        # Procurement statistics
        stats["total_purchase_requests"] = DashboardService._get_total_purchase_requests(db, current_user)
        stats["pending_approvals"] = DashboardService._get_pending_approvals(db, current_user)
        stats["draft_requests"] = DashboardService._get_draft_requests(db, current_user)
        stats["submitted_requests"] = DashboardService._get_submitted_requests(db, current_user)
        
        # RFQ statistics
        stats["total_rfqs"] = DashboardService._get_total_rfqs(db)
        stats["active_rfqs"] = DashboardService._get_active_rfqs(db)
        stats["issued_rfqs"] = DashboardService._get_issued_rfqs(db)
        stats["closed_rfqs"] = DashboardService._get_closed_rfqs(db)
        
        # Quotation statistics
        stats["total_quotations"] = DashboardService._get_total_quotations(db)
        stats["submitted_quotations"] = DashboardService._get_submitted_quotations(db)
        stats["accepted_quotations"] = DashboardService._get_accepted_quotations(db)
        
        # Approval statistics
        stats["pending_approvals_count"] = DashboardService._get_approval_pending_count(db, current_user)
        
        return stats

    @staticmethod
    def _get_total_vendors(db: Session) -> int:
        """Get total number of vendors"""
        return db.query(Vendor).count()

    @staticmethod
    def _get_active_vendors(db: Session) -> int:
        """Get number of active vendors"""
        return db.query(Vendor).filter(
            Vendor.status == VendorStatus.ACTIVE.value
        ).count()

    @staticmethod
    def _get_total_purchase_requests(db: Session, current_user: User) -> int:
        """Get total purchase requests based on user role"""
        query = db.query(PurchaseRequest)
        
        # If not admin/auditor, only show user's own requests
        if current_user.role.name not in ("ADMIN", "AUDITOR"):
            query = query.filter(PurchaseRequest.requester_id == current_user.id)
        
        return query.count()

    @staticmethod
    def _get_pending_approvals(db: Session, current_user: User) -> int:
        """Get number of pending approvals based on user role"""
        query = db.query(PurchaseRequest).filter(
            PurchaseRequest.status == PurchaseRequestStatus.APPROVAL_PENDING.value
        )
        
        # If user has approval permissions, show all
        approval_roles = ["ADMIN", "PROCUREMENT_MANAGER", "PROCUREMENT_HEAD", "FINANCE", "CFO"]
        if current_user.role.name.upper() not in [r.upper() for r in approval_roles]:
            query = query.filter(PurchaseRequest.requester_id == current_user.id)
        
        return query.count()

    @staticmethod
    def _get_draft_requests(db: Session, current_user: User) -> int:
        """Get number of draft requests"""
        query = db.query(PurchaseRequest).filter(
            PurchaseRequest.status == PurchaseRequestStatus.DRAFT.value
        )
        
        if current_user.role.name not in ("ADMIN", "AUDITOR"):
            query = query.filter(PurchaseRequest.requester_id == current_user.id)
        
        return query.count()

    @staticmethod
    def _get_submitted_requests(db: Session, current_user: User) -> int:
        """Get number of submitted requests"""
        query = db.query(PurchaseRequest).filter(
            PurchaseRequest.status == PurchaseRequestStatus.SUBMITTED.value
        )
        
        if current_user.role.name not in ("ADMIN", "AUDITOR"):
            query = query.filter(PurchaseRequest.requester_id == current_user.id)
        
        return query.count()

    @staticmethod
    def _get_total_rfqs(db: Session) -> int:
        """Get total number of RFQs"""
        return db.query(RFQ).count()

    @staticmethod
    def _get_active_rfqs(db: Session) -> int:
        """Get number of active/issued RFQs"""
        return db.query(RFQ).filter(
            RFQ.status.in_([RFQStatus.ISSUED.value, RFQStatus.DRAFT.value])
        ).count()

    @staticmethod
    def _get_issued_rfqs(db: Session) -> int:
        """Get number of issued RFQs"""
        return db.query(RFQ).filter(
            RFQ.status == RFQStatus.ISSUED.value
        ).count()

    @staticmethod
    def _get_closed_rfqs(db: Session) -> int:
        """Get number of closed RFQs"""
        return db.query(RFQ).filter(
            RFQ.status == RFQStatus.CLOSED.value
        ).count()

    @staticmethod
    def _get_total_quotations(db: Session) -> int:
        """Get total number of quotations"""
        return db.query(Quotation).count()

    @staticmethod
    def _get_submitted_quotations(db: Session) -> int:
        """Get number of submitted quotations"""
        return db.query(Quotation).filter(
            Quotation.status == QuotationStatus.SUBMITTED.value
        ).count()

    @staticmethod
    def _get_accepted_quotations(db: Session) -> int:
        """Get number of accepted quotations"""
        return db.query(Quotation).filter(
            Quotation.status == QuotationStatus.ACCEPTED.value
        ).count()

    @staticmethod
    def _get_approval_pending_count(db: Session, current_user: User) -> int:
        """Get number of requests pending approval"""
        query = db.query(PurchaseRequest).filter(
            PurchaseRequest.status == PurchaseRequestStatus.APPROVAL_PENDING.value
        )
        
        # Only users with approval permissions can see all
        approval_roles = ["ADMIN", "PROCUREMENT_MANAGER", "PROCUREMENT_HEAD", "FINANCE", "CFO"]
        if current_user.role.name.upper() not in [r.upper() for r in approval_roles]:
            query = query.filter(PurchaseRequest.requester_id == current_user.id)
        
        return query.count()

    @staticmethod
    def get_recent_activity(
        db: Session,
        current_user: User,
        limit: int = 10
    ) -> list:
        """
        Get recent activity across all modules based on user role
        """
        activities = []

        # Get recent purchase requests
        pr_query = db.query(PurchaseRequest)
        
        if current_user.role.name not in ("ADMIN", "AUDITOR"):
            pr_query = pr_query.filter(PurchaseRequest.requester_id == current_user.id)
        
        pr_query = pr_query.order_by(PurchaseRequest.updated_at.desc()).limit(limit)
        purchase_requests = pr_query.all()
        
        for pr in purchase_requests:
            activities.append({
                "type": "purchase_request",
                "id": pr.id,
                "request_number": pr.request_number,
                "title": pr.title,
                "status": pr.status,
                "timestamp": pr.updated_at,
                "description": f"Purchase request {pr.request_number} updated",
                "user": pr.requester.full_name if pr.requester else "Unknown"
            })

        # Get recent RFQs
        rfq_query = db.query(RFQ).order_by(RFQ.updated_at.desc()).limit(limit)
        rfqs = rfq_query.all()
        
        for rfq in rfqs:
            activities.append({
                "type": "rfq",
                "id": rfq.id,
                "rfq_number": rfq.rfq_number,
                "title": rfq.title,
                "status": rfq.status,
                "timestamp": rfq.updated_at,
                "description": f"RFQ {rfq.rfq_number} updated",
                "user": rfq.created_by_user.full_name if rfq.created_by_user else "Unknown"
            })

        # Get recent quotations
        quotations = db.query(Quotation).order_by(
            Quotation.updated_at.desc()
        ).limit(limit).all()
        
        for quotation in quotations:
            # Get vendor name through rfq_vendor
            vendor_name = "Unknown"
            if quotation.rfq_vendor and quotation.rfq_vendor.vendor:
                vendor_name = quotation.rfq_vendor.vendor.name
            
            activities.append({
                "type": "quotation",
                "id": quotation.id,
                "quotation_number": quotation.quotation_number,
                "vendor": vendor_name,
                "status": quotation.status,
                "timestamp": quotation.updated_at,
                "description": f"Quotation {quotation.quotation_number} from {vendor_name}",
                "user": "Vendor"
            })

        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Return limited results
        return activities[:limit]

    @staticmethod
    def get_dashboard_summary(
        db: Session,
        current_user: User
    ) -> dict:
        """
        Get summary data for dashboard cards
        """
        stats = DashboardService.get_dashboard_stats(db, current_user)
        recent = DashboardService.get_recent_activity(db, current_user)
        
        return {
            "stats": stats,
            "recent_activity": recent,
            "user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "role": current_user.role.name,
                "department": current_user.department.name if current_user.department else None
            }
        }