import re
from typing import Optional, List, Dict, Any, Tuple


class QuotationExtractor:
    """Extract quotation information from user queries."""
    
    # Quotation number patterns - more comprehensive and ordered by specificity
    QUOTATION_PATTERNS = [
        r'QT[-\s\u2011_]*(\d+)',         # QT-000030, QT‑000030, QT_000030, QT 000030
        r'QT(\d{6})',                    # QT000030
        r'QT-?(\d+)',                    # QT-30, QT30 (most flexible)
        r'quotation[:\s#]*(\d+)',        # quotation:30, quotation 30
        r'quote[:\s#]*(\d+)',            # quote:30, quote 30
        r'QT\s*number[:\s#]*(\d+)',      # QT number: 30
    ]
    
    # Direct QT pattern for quick matching
    QT_DIRECT = re.compile(r'QT-?(\d+)', re.IGNORECASE)
    
    # Quotation ID patterns (for when user says "quotation 30" without QT prefix)
    QUOTATION_ID_PATTERNS = [
        r'\b(?:quotation|quote)\s+id\s*[:#-]?\s*(\d+)\b',
        r'\b(?:quotation|quote)\s+number\s*[:#-]?\s*(\d+)\b',
        r'\b(?:quotation|quote)\s+(\d+)\b',  # "quotation 30"
    ]
    
    # Quotation action patterns - more flexible
    APPROVE_PATTERNS = [
        r'approve\s+(?:quotation|quote|QT)',  # approve quotation QT-000030
        r'accept\s+(?:quotation|quote|QT)',   # accept quotation QT-000030
        r'approve\s+QT',                      # approve QT-000030
        r'accept\s+QT',                       # accept QT-000030
        r'approve\s+qt\s*',                   # approve qt 000030
        r'accept\s+qt\s*',                    # accept qt 000030
    ]
    
    REJECT_PATTERNS = [
        r'reject\s+(?:quotation|quote|QT)',   # reject quotation QT-000030
        r'decline\s+(?:quotation|quote|QT)',  # decline quotation QT-000030
        r'reject\s+QT',                       # reject QT-000030
        r'decline\s+QT',                      # decline QT-000030
        r'reject\s+qt\s*',                    # reject qt 000030
        r'decline\s+qt\s*',                   # decline qt 000030
    ]
    
    @staticmethod
    def extract_quotation_id(user_query: str) -> Optional[int]:
        """
        Extract quotation ID from user query.
        Handles formats: QT-000030, QT 000030, QT000030, QT-30, quotation 30
        """
        if not user_query:
            return None
        
        # First try to find QT pattern directly (most common)
        match = QuotationExtractor.QT_DIRECT.search(user_query)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        # Try all patterns
        for pattern in QuotationExtractor.QUOTATION_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        
        # Try quotation ID patterns
        for pattern in QuotationExtractor.QUOTATION_ID_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        
        return None
    
    @staticmethod
    def extract_quotation_number(user_query: str) -> Optional[str]:
        """
        Extract quotation number from user query.
        Returns formatted number like QT-000030.
        """
        if not user_query:
            return None
        
        # Try direct QT pattern first
        match = QuotationExtractor.QT_DIRECT.search(user_query)
        if match:
            qt_num = match.group(1)
            if qt_num.isdigit():
                return f"QT-{qt_num.zfill(6)}"
        
        # Try to extract quotation number with various formats
        for pattern in QuotationExtractor.QUOTATION_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                qt_num = match.group(1)
                # If it's just the number, format it
                if qt_num.isdigit():
                    return f"QT-{qt_num.zfill(6)}"
                # If it's already in QT-XXXXX format
                if qt_num.upper().startswith("QT"):
                    num_match = re.search(r'(\d+)', qt_num)
                    if num_match:
                        return f"QT-{num_match.group(1).zfill(6)}"
                    return qt_num.upper()
                return None
        
        return None
    
    @staticmethod
    def extract_quotation_number_from_operation(operation: str) -> Optional[str]:
        """
        Extract quotation number from operation string.
        Useful when the operation contains quotation info.
        """
        if not operation:
            return None
        
        match = re.search(r'QT[-\s\u2011_]*(\d+)', operation, re.IGNORECASE)
        if match:
            return f"QT-{match.group(1).zfill(6)}"
        
        return None
    
    @staticmethod
    def extract_all_quotations(user_query: str) -> List[str]:
        """
        Extract all quotation numbers from user query.
        """
        if not user_query:
            return []
        
        quotations = []
        for pattern in QuotationExtractor.QUOTATION_PATTERNS:
            matches = re.findall(pattern, user_query, re.IGNORECASE)
            for match in matches:
                if match.isdigit():
                    quotations.append(f"QT-{match.zfill(6)}")
        
        return list(set(quotations))  # Remove duplicates
    
    @staticmethod
    def has_quotation_query(user_query: str) -> bool:
        """
        Check if the user query is about quotations.
        """
        if not user_query:
            return False
        
        quotation_keywords = ['quotation', 'quotations', 'quote', 'quotes', 'qt-', 'qt ', 'qt']
        return any(kw in user_query.lower() for kw in quotation_keywords)
    
    @staticmethod
    def is_quotation_action(user_query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the query is an action on a quotation (approve/reject).
        Returns (is_action, action_type) where action_type is 'approve' or 'reject'.
        """
        if not user_query:
            return False, None
        
        query_lower = user_query.lower()
        
        # Check if it's an approve action
        for pattern in QuotationExtractor.APPROVE_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True, 'approve'
        
        # Check if it's a reject action
        for pattern in QuotationExtractor.REJECT_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True, 'reject'
        
        return False, None
    
    @staticmethod
    def is_quotation_list_query(user_query: str) -> bool:
        """
        Check if the query is asking for a list of quotations.
        """
        if not user_query:
            return False
        
        list_keywords = ['list', 'show', 'all', 'recent', 'existing', 'get', 'fetch']
        quotation_keywords = ['quotation', 'quotations', 'quote', 'quotes']
        
        query_lower = user_query.lower()
        has_list = any(kw in query_lower for kw in list_keywords)
        has_quotation = any(kw in query_lower for kw in quotation_keywords)
        
        return has_list and has_quotation
    
    @staticmethod
    def is_quotation_compare_query(user_query: str) -> bool:
        """
        Check if the query is asking to compare quotations.
        """
        if not user_query:
            return False
        
        compare_keywords = ['compare', 'comparison', 'versus', 'vs']
        query_lower = user_query.lower()
        
        has_compare = any(kw in query_lower for kw in compare_keywords)
        has_quotation = QuotationExtractor.has_quotation_query(user_query)
        
        return has_compare and has_quotation
    
    @staticmethod
    def extract_quotation_id_from_any(user_query: str) -> Optional[int]:
        """
        Fallback method that tries absolutely everything to extract a quotation ID.
        """
        if not user_query:
            return None
        
        # Try to find QT number anywhere in the query
        qt_match = QuotationExtractor.QT_DIRECT.search(user_query)
        if qt_match:
            try:
                return int(qt_match.group(1))
            except ValueError:
                pass
        
        # Try to find any number after "quotation" or "quote"
        for pattern in QuotationExtractor.QUOTATION_ID_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        # Try to find any number in the query (last resort)
        numbers = re.findall(r'\b(\d+)\b', user_query)
        if numbers:
            # If there's only one number, assume it's the quotation ID
            if len(numbers) == 1:
                try:
                    return int(numbers[0])
                except ValueError:
                    pass
        
        return None