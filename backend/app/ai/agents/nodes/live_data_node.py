import json
from typing import Dict, Any
import logging

from app.ai.agents.state import ProcureOpsState
from app.ai.mcp.client.procureops_client import ProcureOpsMCPClient
from app.ai.mcp.tools.tool_mapper import MCPToolMapper
from app.ai.services.operation_resolver import OperationType

logger = logging.getLogger(__name__)


async def live_data_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Handle live data operations using MCP tools.
    """
    operation = state.get("operation")
    entities = state.get("entities", {})
    user_query = state.get("user_query", "")
    
    logger.info(f"Live Data Node: {operation}")
    
    # ============================================================
    # GET MCP TOOL
    # ============================================================
    
    tool_config = MCPToolMapper.get_tool(operation, entities)
    tool_name = tool_config.get("tool_name")
    arguments = tool_config.get("arguments", {})
    
    if not tool_name:
        return {
            "response": f"I couldn't determine how to handle '{operation}'.",
            "live_data": None,
            "sources": [],
        }
    
    logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")
    
    # ============================================================
    # CALL MCP TOOL
    # ============================================================
    
    mcp_response = await ProcureOpsMCPClient.call_tool(tool_name, arguments)
    
    if not mcp_response.get("success"):
        error_msg = mcp_response.get("error", "Unknown error")
        return {
            "response": f"Unable to retrieve data: {error_msg}",
            "live_data": None,
            "sources": [],
            "error": error_msg,
        }
    
    live_data = mcp_response.get("data")
    
    if live_data is None:
        return {
            "response": "No data found.",
            "live_data": None,
            "sources": [],
        }
    
    # ============================================================
    # CHECK IF RESOURCE WAS FOUND
    # ============================================================
    
    if isinstance(live_data, dict) and live_data.get("found") is False:
        return {
            "response": live_data.get("message", "Resource not found."),
            "live_data": live_data,
            "sources": [],
        }
    
    # ============================================================
    # FORMAT RESPONSE BASED ON OPERATION
    # ============================================================
    
    formatted_response = _format_live_data(operation, live_data, user_query)
    
    return {
        "response": formatted_response,
        "live_data": live_data,
        "sources": [{"source": tool_name, "operation": operation}],
    }


def _format_live_data(operation: str, data: Any, user_query: str) -> str:
    """Format live data based on operation type."""
    
    # For list operations, format directly (no LLM needed)
    list_operations = {
        OperationType.GET_RFQS: _format_rfq_list,
        OperationType.GET_QUOTATIONS: _format_quotation_list,
        OperationType.SEARCH_VENDORS: _format_vendor_list,
        OperationType.GET_PROCUREMENT_REQUESTS: _format_procurement_list,
        OperationType.GET_APPROVALS: _format_approval_list,
    }
    
    if operation in list_operations:
        return list_operations[operation](data)
    
    # For details, include formatted output
    if operation == OperationType.GET_RFQ_DETAILS:
        return _format_rfq_details(data)
    
    if operation == OperationType.GET_QUOTATION_DETAILS:
        return _format_quotation_details(data)
    
    if operation == OperationType.COMPARE_QUOTATIONS:
        return _format_comparison(data)
    
    if operation in [OperationType.APPROVE_QUOTATION, OperationType.REJECT_QUOTATION]:
        return _format_action_result(data)
    
    # Default: JSON string
    try:
        return json.dumps(data, indent=2, default=str)[:2000]
    except:
        return str(data)


def _format_rfq_list(data: Dict) -> str:
    """Format RFQ list."""
    if not data:
        return "No RFQs found."
    
    rfqs = data.get("rfqs", data) if isinstance(data, dict) else data
    if not rfqs:
        return "No RFQs found."
    
    result = "Here are the recent RFQs:\n\n"
    for rfq in rfqs[:10]:
        result += f"**{rfq.get('rfq_number')}** - {rfq.get('title')}\n"
        result += f"  Status: {rfq.get('status')}\n"
        result += f"  Items: {len(rfq.get('items', []))}\n\n"
    
    if len(rfqs) > 10:
        result += f"... and {len(rfqs) - 10} more RFQs."
    
    return result


def _format_quotation_list(data: Dict) -> str:
    """Format quotation list."""
    if not data:
        return "No quotations found."
    
    quotations = data.get("quotations", data) if isinstance(data, dict) else data
    if not quotations:
        return "No quotations found."
    
    result = "Here are the existing quotations:\n\n"
    for q in quotations[:10]:
        vendor = q.get('vendor_name', 'Unknown Vendor')
        result += f"**{q.get('quotation_number')}** - {vendor}\n"
        result += f"  Amount: {q.get('currency', 'INR')} {q.get('total_amount', 0):,.2f}\n"
        result += f"  Status: {q.get('status')}\n\n"
    
    if len(quotations) > 10:
        result += f"... and {len(quotations) - 10} more quotations."
    
    return result


def _format_vendor_list(data: Dict) -> str:
    """Format vendor list."""
    if not data:
        return "No vendors found."
    
    vendors = data.get("vendors", data) if isinstance(data, dict) else data
    if not vendors:
        return "No vendors found."
    
    result = "Here are the vendors:\n\n"
    for v in vendors[:10]:
        result += f"**{v.get('name')}** ({v.get('vendor_code')})\n"
        result += f"  Status: {v.get('status')}\n"
        result += f"  Email: {v.get('email')}\n\n"
    
    if len(vendors) > 10:
        result += f"... and {len(vendors) - 10} more vendors."
    
    return result


def _format_procurement_list(data: Dict) -> str:
    """Format procurement request list."""
    if not data:
        return "No procurement requests found."
    
    requests = data.get("requests", data) if isinstance(data, dict) else data
    if not requests:
        return "No procurement requests found."
    
    result = "Here are the procurement requests:\n\n"
    for req in requests[:10]:
        result += f"**{req.get('request_number')}** - {req.get('title')}\n"
        result += f"  Status: {req.get('status')}\n"
        result += f"  Amount: {req.get('currency', 'INR')} {req.get('estimated_amount', 0):,.2f}\n\n"
    
    if len(requests) > 10:
        result += f"... and {len(requests) - 10} more requests."
    
    return result


def _format_approval_list(data: Dict) -> str:
    """Format approval list."""
    if not data:
        return "No pending approvals found."
    
    approvals = data.get("approvals", data) if isinstance(data, dict) else data
    if not approvals:
        return "No pending approvals found."
    
    result = "Here are your pending approvals:\n\n"
    for approval in approvals[:10]:
        result += f"**{approval.get('request_number')}** - {approval.get('title')}\n"
        result += f"  Required Role: {approval.get('required_role')}\n"
        result += f"  Amount: {approval.get('currency', 'INR')} {approval.get('estimated_amount', 0):,.2f}\n\n"
    
    if len(approvals) > 10:
        result += f"... and {len(approvals) - 10} more approvals."
    
    return result


def _format_rfq_details(data: Dict) -> str:
    """Format RFQ details."""
    if not data:
        return "RFQ not found."
    
    rfq = data.get("rfq", data) if isinstance(data, dict) else data
    
    result = f"**{rfq.get('rfq_number')}** - {rfq.get('title')}\n\n"
    result += f"**Status:** {rfq.get('status')}\n"
    if rfq.get('description'):
        result += f"**Description:** {rfq.get('description')}\n"
    if rfq.get('submission_deadline'):
        result += f"**Submission Deadline:** {rfq.get('submission_deadline')}\n"
    if rfq.get('issue_date'):
        result += f"**Issue Date:** {rfq.get('issue_date')}\n"
    
    items = rfq.get('items', [])
    if items:
        result += f"\n**Items ({len(items)}):**\n"
        for item in items[:10]:
            result += f"  - {item.get('item_name')}: {item.get('quantity')} {item.get('unit')}\n"
            if item.get('description'):
                result += f"    {item.get('description')}\n"
    
    vendors = rfq.get('vendors', [])
    if vendors:
        result += f"\n**Vendors ({len(vendors)}):**\n"
        for vendor in vendors[:10]:
            result += f"  - Vendor #{vendor.get('vendor_id')}: {vendor.get('status')}\n"
    
    return result


def _format_quotation_details(data: Dict) -> str:
    """Format quotation details."""
    if not data:
        return "Quotation not found."
    
    q = data.get("quotation", data) if isinstance(data, dict) else data
    
    result = f"**{q.get('quotation_number')}**\n\n"
    result += f"**Vendor:** {q.get('vendor_name', 'Unknown')}\n"
    result += f"**Status:** {q.get('status')}\n"
    result += f"**Total Amount:** {q.get('currency', 'INR')} {q.get('total_amount', 0):,.2f}\n"
    if q.get('submitted_at'):
        result += f"**Submitted:** {q.get('submitted_at')}\n"
    if q.get('valid_until'):
        result += f"**Valid Until:** {q.get('valid_until')}\n"
    
    items = q.get('items', [])
    if items:
        result += f"\n**Items ({len(items)}):**\n"
        for item in items[:10]:
            result += f"  - {item.get('item_name')}: {item.get('quantity')} {item.get('unit')}\n"
            result += f"    Unit Price: {q.get('currency', 'INR')} {item.get('unit_price', 0):,.2f}\n"
            result += f"    Total: {q.get('currency', 'INR')} {item.get('total_price', 0):,.2f}\n"
    
    return result


def _format_comparison(data: Dict) -> str:
    """Format comparison data."""
    if not data:
        return "No comparison data available."
    
    result = f"**{data.get('rfq_number')}** - {data.get('title')}\n\n"
    
    # Quotation summaries
    quotations = data.get('quotations', [])
    if quotations:
        result += "**Quotation Summary:**\n\n"
        for q in quotations:
            rank = q.get('rank', 'N/A')
            vendor = q.get('vendor_name', 'Unknown')
            amount = q.get('total_amount', 0)
            currency = q.get('currency', 'INR')
            result += f"  #{rank}: {vendor} - {currency} {amount:,.2f}\n"
    
    # Item comparison
    items = data.get('item_comparison', [])
    if items:
        result += "\n**Item-wise Comparison:**\n\n"
        for item in items:
            result += f"  **{item.get('item_name')}** ({item.get('quantity')} {item.get('unit')})\n"
            prices = item.get('prices', [])
            for price in prices:
                vendor = price.get('vendor_name', 'Unknown')
                total = price.get('total_price', 0)
                unit = price.get('unit_price', 0)
                result += f"    - {vendor}: Total {currency} {total:,.2f} (Unit: {currency} {unit:,.2f})\n"
    
    return result


def _format_action_result(data: Dict) -> str:
    """Format action result (approve/reject)."""
    if not data:
        return "Action completed."
    
    success = data.get('success', False)
    message = data.get('message', '')
    quotation = data.get('quotation', {})
    
    if success:
        result = f"✅ {message}\n\n"
    else:
        result = f"❌ {message}\n\n"
    
    if quotation:
        result += f"**Quotation:** {quotation.get('quotation_number')}\n"
        result += f"**Status:** {quotation.get('status')}\n"
        if quotation.get('previous_status'):
            result += f"**Previous Status:** {quotation.get('previous_status')}\n"
        if quotation.get('total_amount'):
            result += f"**Amount:** {quotation.get('currency', 'INR')} {quotation.get('total_amount', 0):,.2f}\n"
    
    return result