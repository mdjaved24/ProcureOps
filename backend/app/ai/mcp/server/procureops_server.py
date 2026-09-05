from mcp.server import MCPServer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.ai.mcp.tools.rfq_service import RFQMCPService
from app.ai.mcp.tools.quotation_service import QuotationMCPService
from app.ai.mcp.tools.vendor_service import VendorMCPService
from app.ai.mcp.tools.procurement_service import ProcurementMCPService
from app.ai.mcp.tools.approval_service import ApprovalMCPService
from app.ai.mcp.tools.action_service import ActionMCPService


# ============================================================
# CREATE MCP SERVER
# ============================================================

mcp = MCPServer(
    name="ProcureOps MCP Server",
)


def get_db() -> Session:
    """Get database session."""
    return SessionLocal()


# ============================================================
# RFQ TOOLS
# ============================================================

@mcp.tool()
def get_rfqs(limit: int = 10) -> dict:
    """
    Get a list of RFQs.
    
    Args:
        limit: Maximum number of RFQs to return (default: 10)
    
    Returns:
        dict: List of RFQs with their details
    """
    db = get_db()
    try:
        return RFQMCPService.get_rfqs(db, limit)
    finally:
        db.close()


@mcp.tool()
def get_rfq_details(rfq_id: int) -> dict:
    """
    Get detailed information about a specific RFQ.
    
    Args:
        rfq_id: ID of the RFQ to retrieve
    
    Returns:
        dict: Complete RFQ details including items and vendors
    """
    db = get_db()
    try:
        return RFQMCPService.get_rfq_details(db, rfq_id)
    finally:
        db.close()


@mcp.tool()
def get_rfq_status(rfq_id: int) -> dict:
    """
    Get the status of a specific RFQ.
    
    Args:
        rfq_id: ID of the RFQ to check
    
    Returns:
        dict: RFQ status information
    """
    db = get_db()
    try:
        return RFQMCPService.get_rfq_status(db, rfq_id)
    finally:
        db.close()


# ============================================================
# QUOTATION TOOLS
# ============================================================

@mcp.tool()
def get_quotations() -> dict:
    """
    Get all quotations.
    
    Returns:
        dict: List of all quotations with vendor information
    """
    db = get_db()
    try:
        return QuotationMCPService.get_quotations(db)
    finally:
        db.close()


@mcp.tool()
def get_rfq_quotations(rfq_number: str) -> dict:
    """
    Get quotations for a specific RFQ.
    
    Args:
        rfq_number: RFQ number (e.g., RFQ-000039)
    
    Returns:
        dict: Quotations for the RFQ with item details
    """
    db = get_db()
    try:
        return QuotationMCPService.get_rfq_quotations(db, rfq_number)
    finally:
        db.close()


@mcp.tool()
def get_quotation_details(quotation_id: int) -> dict:
    """
    Get detailed information about a specific quotation.
    
    Args:
        quotation_id: ID of the quotation to retrieve
    
    Returns:
        dict: Complete quotation details including items
    """
    db = get_db()
    try:
        return QuotationMCPService.get_quotation_details(db, quotation_id)
    finally:
        db.close()


@mcp.tool()
def compare_rfq_quotations(rfq_number: str) -> dict:
    """
    Compare all quotations for a closed RFQ.
    
    Args:
        rfq_number: RFQ number (e.g., RFQ-000039)
    
    Returns:
        dict: Comparison of quotations with rankings and item prices
    """
    db = get_db()
    try:
        return QuotationMCPService.compare_rfq_quotations(db, rfq_number)
    finally:
        db.close()


# ============================================================
# VENDOR TOOLS
# ============================================================

@mcp.tool()
def search_vendors(search: str = None, limit: int = 10) -> dict:
    """
    Search for vendors by name, code, email, or city.
    
    Args:
        search: Search term (optional)
        limit: Maximum number of vendors to return (default: 10)
    
    Returns:
        dict: List of matching vendors
    """
    db = get_db()
    try:
        return VendorMCPService.search_vendors(db, search, limit)
    finally:
        db.close()


@mcp.tool()
def get_vendor(vendor_id: int = None, vendor_code: str = None) -> dict:
    """
    Get vendor details by ID or code.
    
    Args:
        vendor_id: Vendor ID (optional)
        vendor_code: Vendor code (optional)
    
    Returns:
        dict: Complete vendor details
    """
    db = get_db()
    try:
        return VendorMCPService.get_vendor(db, vendor_id, vendor_code)
    finally:
        db.close()


# ============================================================
# PROCUREMENT TOOLS
# ============================================================

@mcp.tool()
def get_procurement_requests(limit: int = 10) -> dict:
    """
    Get procurement requests.
    
    Args:
        limit: Maximum number of requests to return (default: 10)
    
    Returns:
        dict: List of procurement requests
    """
    db = get_db()
    try:
        return ProcurementMCPService.get_procurement_requests(db, limit)
    finally:
        db.close()


@mcp.tool()
def get_pr_details(pr_id: int) -> dict:
    """
    Get details of a specific procurement request.
    
    Args:
        pr_id: ID of the procurement request
    
    Returns:
        dict: Complete PR details including items
    """
    db = get_db()
    try:
        return ProcurementMCPService.get_pr_details(db, pr_id)
    finally:
        db.close()


# ============================================================
# APPROVAL TOOLS
# ============================================================

@mcp.tool()
def get_approvals() -> dict:
    """
    Get pending approvals.
    
    Returns:
        dict: List of pending approvals
    """
    db = get_db()
    try:
        return ApprovalMCPService.get_approvals(db)
    finally:
        db.close()


# ============================================================
# ACTION TOOLS (HITL)
# ============================================================

@mcp.tool()
def approve_quotation(quotation_id: int) -> dict:
    """
    Approve a submitted quotation.
    
    This is a sensitive action that requires HITL approval.
    
    Args:
        quotation_id: ID of the quotation to approve
    
    Returns:
        dict: Result of the approval action
    """
    db = get_db()
    try:
        # This will be called after HITL approval
        return ActionMCPService.approve_quotation(db, quotation_id)
    finally:
        db.close()


@mcp.tool()
def reject_quotation(quotation_id: int) -> dict:
    """
    Reject a submitted quotation.
    
    This is a sensitive action that requires HITL approval.
    
    Args:
        quotation_id: ID of the quotation to reject
    
    Returns:
        dict: Result of the rejection action
    """
    db = get_db()
    try:
        return ActionMCPService.reject_quotation(db, quotation_id)
    finally:
        db.close()


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()