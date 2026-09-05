from typing import Dict, Any, Optional, Tuple
from app.ai.mcp.tools.rfq_extractor import RFQExtractor
from app.ai.mcp.tools.vendor_extractor import VendorExtractor
from app.ai.mcp.tools.quotation_extractor import QuotationExtractor


class EntityExtractor:
    """
    Unified entity extractor that combines all extractors.
    """
    
    @staticmethod
    def extract_all(user_query: str) -> Dict[str, Any]:
        """
        Extract all entities from user query.
        """
        if not user_query:
            return {}
        
        is_quotation_action_result = QuotationExtractor.is_quotation_action(user_query)
        if isinstance(is_quotation_action_result, tuple):
            is_quotation_action, action_type = is_quotation_action_result
        else:
            is_quotation_action = False
            action_type = None
        
        return {
            # RFQ
            "rfq_number": RFQExtractor.extract_rfq_number(user_query),
            "rfq_id": RFQExtractor.extract_rfq_id(user_query),
            "has_rfq": RFQExtractor.has_rfq_query(user_query),
            "is_rfq_list": RFQExtractor.is_rfq_list_query(user_query),
            "is_rfq_details": RFQExtractor.is_rfq_details_query(user_query),
            
            # PR
            "pr_number": RFQExtractor.extract_pr_number(user_query),
            "pr_id": RFQExtractor.extract_pr_id(user_query),
            
            # Vendor
            "vendor_id": VendorExtractor.extract_vendor_id(user_query),
            "vendor_code": VendorExtractor.extract_vendor_code(user_query),
            "vendor_status": VendorExtractor.extract_vendor_status(user_query),
            "vendor_search": VendorExtractor.extract_vendor_search(user_query),
            "vendor_name": VendorExtractor.extract_vendor_name(user_query),
            "has_vendor": VendorExtractor.has_vendor_query(user_query),
            "is_vendor_list": VendorExtractor.is_vendor_list_query(user_query),
            
            # Quotation
            "quotation_id": QuotationExtractor.extract_quotation_id(user_query),
            "quotation_number": QuotationExtractor.extract_quotation_number(user_query),
            "has_quotation": QuotationExtractor.has_quotation_query(user_query),
            "is_quotation_list": QuotationExtractor.is_quotation_list_query(user_query),
            "is_quotation_compare": QuotationExtractor.is_quotation_compare_query(user_query),
            "is_quotation_action": is_quotation_action,
            "quotation_action_type": action_type,
        }