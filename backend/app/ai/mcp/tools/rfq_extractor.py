import re
from typing import Optional, List, Dict, Any


class RFQExtractor:
    """Extract RFQ information from user queries."""
    
    # RFQ number patterns
    RFQ_PATTERNS = [
        r'RFQ[-\s]*(\d+)',           # RFQ-000039, RFQ 000039
        r'RFQ[:\s#]*(\d+)',          # RFQ:000039, RFQ #000039
        r'request for quotation[:\s#]*(\d+)',  # request for quotation 000039
        r'rfq\s*number[:\s#]*(\d+)', # rfq number: 000039
    ]
    
    @staticmethod
    def extract_rfq_number(user_query: str) -> Optional[str]:
        """
        Extract RFQ number from user query.
        Returns formatted RFQ number like RFQ-000039.
        """
        if not user_query:
            return None
        
        for pattern in RFQExtractor.RFQ_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                rfq_num = match.group(1)
                return f"RFQ-{rfq_num.zfill(6)}"
        
        return None
    
    @staticmethod
    def extract_rfq_id(user_query: str) -> Optional[int]:
        """
        Extract RFQ numeric ID from user query.
        """
        if not user_query:
            return None
        
        for pattern in RFQExtractor.RFQ_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        
        return None
    
    @staticmethod
    def extract_all_rfqs(user_query: str) -> List[str]:
        """
        Extract all RFQ numbers from user query.
        """
        if not user_query:
            return []
        
        rfqs = []
        for pattern in RFQExtractor.RFQ_PATTERNS:
            matches = re.findall(pattern, user_query, re.IGNORECASE)
            for match in matches:
                rfqs.append(f"RFQ-{match.zfill(6)}")
        
        return list(set(rfqs))  # Remove duplicates
    
    @staticmethod
    def has_rfq_query(user_query: str) -> bool:
        """
        Check if the query is about RFQs.
        """
        if not user_query:
            return False
        
        rfq_keywords = ['rfq', 'request for quotation', 'rfqs']
        return any(kw in user_query.lower() for kw in rfq_keywords)
    
    @staticmethod
    def is_rfq_list_query(user_query: str) -> bool:
        """
        Check if the query is asking for a list of RFQs.
        """
        if not user_query:
            return False
        
        list_keywords = ['list', 'show', 'all', 'recent', 'existing', 'get', 'fetch']
        rfq_keywords = ['rfq', 'rfqs', 'request for quotation']
        
        query_lower = user_query.lower()
        has_list = any(kw in query_lower for kw in list_keywords)
        has_rfq = any(kw in query_lower for kw in rfq_keywords)
        
        return has_list and has_rfq
    
    @staticmethod
    def is_rfq_details_query(user_query: str) -> bool:
        """
        Check if the query is asking for RFQ details.
        """
        if not user_query:
            return False
        
        detail_keywords = ['details', 'detail', 'about', 'information', 'info', 'view', 'show']
        query_lower = user_query.lower()
        
        has_detail = any(kw in query_lower for kw in detail_keywords)
        has_rfq = RFQExtractor.has_rfq_query(user_query)
        
        return has_detail and has_rfq


    # PR number patterns
    PR_PATTERNS = [
        r'PR[-\s]*(\d+)',           # PR-000001, PR 000001
        r'purchase request[:\s#]*(\d+)',  # purchase request 1
    ]
    
    @staticmethod
    def extract_pr_number(user_query: str) -> Optional[str]:
        """
        Extract PR number from user query.
        Returns formatted PR number like PR-000001.
        """
        if not user_query:
            return None
        
        for pattern in RFQExtractor.PR_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                pr_num = match.group(1)
                return f"PR-{pr_num.zfill(6)}"
        
        return None
    
    @staticmethod
    def extract_pr_id(user_query: str) -> Optional[int]:
        """
        Extract PR numeric ID from user query.
        """
        if not user_query:
            return None
        
        for pattern in RFQExtractor.PR_PATTERNS:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        
        return None