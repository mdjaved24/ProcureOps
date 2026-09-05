from typing import Dict, Any, Optional
from app.ai.services.operation_resolver import OperationType


class MCPToolMapper:
    """
    Maps operations to MCP tools with argument extraction.
    """
    
    # Operation → (tool_name, argument_template)
    TOOL_MAP = {
        # RFQ Operations
        OperationType.GET_RFQS: ("get_rfqs", {}),
        OperationType.GET_RFQ_DETAILS: ("get_rfq_details", {"rfq_id": "entity"}),
        OperationType.GET_RFQ_STATUS: ("get_rfq_details", {"rfq_id": "entity"}),
        
        # Quotation Operations
        OperationType.GET_QUOTATIONS: ("get_quotations", {}),
        OperationType.GET_RFQ_QUOTATIONS: ("get_rfq_quotations", {"rfq_number": "entity"}),
        OperationType.GET_QUOTATION_DETAILS: ("get_quotation_details", {"quotation_id": "entity"}),
        OperationType.COMPARE_QUOTATIONS: ("compare_rfq_quotations", {"rfq_number": "entity"}),
        OperationType.APPROVE_QUOTATION: ("approve_quotation", {"quotation_id": "entity"}),
        OperationType.REJECT_QUOTATION: ("reject_quotation", {"quotation_id": "entity"}),
        
        # Vendor Operations
        OperationType.SEARCH_VENDORS: ("search_vendors", {"search": "entity"}),
        OperationType.GET_VENDOR: ("get_vendor", {"vendor_id": "entity"}),
        OperationType.GET_VENDOR_DETAILS: ("get_vendor", {"vendor_id": "entity"}),
        
        # Procurement Operations
        OperationType.GET_PROCUREMENT_REQUESTS: ("get_procurement_requests", {}),
        OperationType.GET_PROCUREMENT_REQUEST_DETAILS: ("get_pr_details", {"pr_id": "entity"}),
        
        # Approval Operations
        OperationType.GET_APPROVALS: ("get_approvals", {}),
    }
    
    @classmethod
    def get_tool(cls, operation: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get tool name and arguments for an operation.
        """
        if operation not in cls.TOOL_MAP:
            return {"tool_name": None, "arguments": {}}
        
        tool_name, arg_template = cls.TOOL_MAP[operation]
        arguments = {}
        
        # Build arguments from template and entities
        for key, value in arg_template.items():
            if value == "entity":
                entity_value = cls._extract_entity(key, entities)
                if entity_value is not None:
                    arguments[key] = entity_value
            else:
                arguments[key] = value
        
        return {
            "tool_name": tool_name,
            "arguments": arguments
        }
    
    @classmethod
    def _extract_entity(cls, key: str, entities: Dict[str, Any]) -> Optional[Any]:
        """Extract entity value from entities dict."""
        # Direct match
        if key in entities:
            return entities[key]
        
        # Try variations
        variations = {
            "rfq_id": ["rfq_id", "rfq_number", "rfq_num"],
            "rfq_number": ["rfq_number", "rfq_id", "rfq_num"],
            "quotation_id": ["quotation_id", "quotation_number", "qt_id", "qt_num"],
            "vendor_id": ["vendor_id", "vendor_code"],
            "pr_id": ["pr_id", "pr_number"],
            "search": ["vendor_search", "search", "query"],
        }
        
        for var in variations.get(key, []):
            if var in entities:
                return entities[var]
        
        return None