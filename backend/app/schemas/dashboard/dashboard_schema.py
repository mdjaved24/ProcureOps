from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    model_config = ConfigDict(from_attributes=True)
    
    # Vendor statistics
    total_vendors: int = 0
    active_vendors: int = 0
    
    # Procurement statistics
    total_purchase_requests: int = 0
    pending_approvals: int = 0
    draft_requests: int = 0
    submitted_requests: int = 0
    
    # RFQ statistics
    total_rfqs: int = 0
    active_rfqs: int = 0
    issued_rfqs: int = 0
    closed_rfqs: int = 0
    
    # Quotation statistics
    total_quotations: int = 0
    submitted_quotations: int = 0
    accepted_quotations: int = 0
    
    # Approval statistics
    pending_approvals_count: int = 0


class RecentActivityItem(BaseModel):
    """Individual activity item"""
    model_config = ConfigDict(from_attributes=True)
    
    type: str  # purchase_request, rfq, quotation, etc.
    id: int
    request_number: Optional[str] = None
    rfq_number: Optional[str] = None
    quotation_number: Optional[str] = None
    title: Optional[str] = None
    vendor: Optional[str] = None
    status: str
    timestamp: datetime
    description: str
    user: str


class DashboardSummaryResponse(BaseModel):
    """Complete dashboard response"""
    model_config = ConfigDict(from_attributes=True)
    
    stats: DashboardStats
    recent_activity: list[RecentActivityItem]
    user: dict