import re
from typing import Optional, List, Dict, Any


class VendorExtractor:
    """Extract vendor information from user queries."""
    
    # Vendor ID patterns
    VENDOR_ID_PATTERNS = [
        r'vendor[:\s#]*(\d+)',           # vendor:123, vendor 123, vendor#123
        r'vendors?[:\s#]*(\d+)',         # vendor:123, vendors 123
        r'V[-\s]*(\d+)',                 # V-123, V 123
        r'supplier[:\s#]*(\d+)',         # supplier:123
    ]
    
    # Vendor code patterns
    VENDOR_CODE_PATTERNS = [
        r'vendor code[:\s]*([A-Z0-9\-_]+)',  # vendor code: VEN-001
        r'vendor_code[:\s]*([A-Z0-9\-_]+)',  # vendor_code: VEN-001
        r'code[:\s]*([A-Z0-9\-_]+)',         # code: VEN-001
        r'vendor[:\s]*([A-Z]{3,5}-[0-9]{3})', # VEN-001
    ]
    
    # Vendor status patterns
    VENDOR_STATUS_PATTERNS = {
        'ACTIVE': r'\b(active|activated|enabled|approved)\b',
        'INACTIVE': r'\b(inactive|deactivated|disabled|suspended)\b',
        'BLOCKED': r'\b(blocked|banned|blacklisted)\b',
        'PENDING': r'\b(pending|under review|review)\b',
    }
    
    # Vendor search patterns
    VENDOR_SEARCH_PATTERNS = [
        r'(?:search|find|show|list|get)\s+(?:for\s+)?(?:vendor|vendors?)\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?',
        r'vendor\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?',
        r'supplier\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?',
    ]
    
    @staticmethod
    def extract_vendor_id(user_query: str) -> Optional[int]:
        """
        Extract vendor ID from user query.
        """
        if not user_query:
            return None
        
        for pattern in VendorExtractor.VENDOR_ID_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        
        return None
    
    @staticmethod
    def extract_vendor_code(user_query: str) -> Optional[str]:
        """
        Extract vendor code from user query.
        """
        if not user_query:
            return None
        
        for pattern in VendorExtractor.VENDOR_CODE_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                return match.group(1).strip().upper()
        
        return None
    
    @staticmethod
    def extract_vendor_status(user_query: str) -> Optional[str]:
        """
        Extract vendor status from user query.
        """
        if not user_query:
            return None
        
        query_lower = user_query.lower()
        for status, pattern in VendorExtractor.VENDOR_STATUS_PATTERNS.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                return status
        
        return None
    
    @staticmethod
    def extract_vendor_search(user_query: str) -> Optional[str]:
        """
        Extract vendor search term from user query.
        """
        if not user_query:
            return None
        
        # Pattern 1: "Search for ABC Supplies"
        match = re.search(r'(?:search|find)\s+(?:for\s+)?([a-zA-Z0-9\s\-_&.]+)', user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: "ABC Supplies" after vendor
        match = re.search(r'vendor\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?', user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 3: "ABC Supplies" after search/find
        match = re.search(r'(?:search|find|show|list|get)\s+(?:vendor|vendors?)\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?', user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_vendor_name(user_query: str) -> Optional[str]:
        """
        Extract vendor name from user query.
        """
        if not user_query:
            return None
        
        # Try to extract from search patterns
        search_term = VendorExtractor.extract_vendor_search(user_query)
        if search_term:
            return search_term
        
        # Try direct pattern: "vendor ABC Supplies"
        match = re.search(r'vendor\s+["\']?([a-zA-Z0-9\s\-_&.]+)["\']?', user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def has_vendor_query(user_query: str) -> bool:
        """
        Check if the query is about vendors.
        """
        if not user_query:
            return False
        
        vendor_keywords = ['vendor', 'vendors', 'supplier', 'suppliers', 'supply']
        return any(kw in user_query.lower() for kw in vendor_keywords)
    
    @staticmethod
    def is_vendor_list_query(user_query: str) -> bool:
        """
        Check if the query is asking for a list of vendors.
        """
        if not user_query:
            return False
        
        list_keywords = ['list', 'show', 'all', 'recent', 'existing', 'get', 'fetch']
        vendor_keywords = ['vendor', 'vendors', 'supplier', 'suppliers']
        
        query_lower = user_query.lower()
        has_list = any(kw in query_lower for kw in list_keywords)
        has_vendor = any(kw in query_lower for kw in vendor_keywords)
        
        return has_list and has_vendor