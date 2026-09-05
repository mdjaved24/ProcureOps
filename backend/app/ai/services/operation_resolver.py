import json
import logging
import re
from typing import Dict, Any, Optional
from enum import Enum

from app.ai.llm.groq_llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class OperationType:
    """Operation types for the AI agent."""
    # RFQ Operations
    GET_RFQS = "GET_RFQS"
    GET_RFQ_DETAILS = "GET_RFQ_DETAILS"
    GET_RFQ_STATUS = "GET_RFQ_STATUS"
    
    # Quotation Operations
    GET_QUOTATIONS = "GET_QUOTATIONS"
    GET_RFQ_QUOTATIONS = "GET_RFQ_QUOTATIONS"
    GET_QUOTATION_DETAILS = "GET_QUOTATION_DETAILS"
    COMPARE_QUOTATIONS = "COMPARE_QUOTATIONS"
    APPROVE_QUOTATION = "APPROVE_QUOTATION"
    REJECT_QUOTATION = "REJECT_QUOTATION"
    
    # Vendor Operations
    SEARCH_VENDORS = "SEARCH_VENDORS"
    GET_VENDOR = "GET_VENDOR"
    GET_VENDOR_DETAILS = "GET_VENDOR_DETAILS"
    
    # Procurement Operations
    GET_PROCUREMENT_REQUESTS = "GET_PROCUREMENT_REQUESTS"
    GET_PROCUREMENT_REQUEST_DETAILS = "GET_PROCUREMENT_REQUEST_DETAILS"
    
    # Approval Operations
    GET_APPROVALS = "GET_APPROVALS"
    
    # Knowledge/General
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"
    FOLLOW_UP = "FOLLOW_UP"


class OperationResolver:
    """
    LLM-based operation resolver - more flexible and accurate than regex.
    Uses structured output from LLM to classify operations.
    """

    # ============================================================
    # SYSTEM PROMPT
    # ============================================================

    SYSTEM_PROMPT = """
    You are an operation classifier for a procurement AI assistant called ProcureOps.

    Classify the user's query into exactly one of these operations:

    RFQ OPERATIONS:
    - GET_RFQS: User wants to list or see RFQs (e.g., "Show me RFQs", "List all RFQs")
    - GET_RFQ_DETAILS: User wants details of a specific RFQ (needs RFQ number, e.g., "Show RFQ-000039")
    - GET_RFQ_STATUS: User wants status of an RFQ (needs RFQ number, e.g., "What is RFQ-000039 status?")

    QUOTATION OPERATIONS:
    - GET_QUOTATIONS: User wants to list all quotations (e.g., "Show me quotations", "What are existing quotations?")
    - GET_RFQ_QUOTATIONS: User wants quotations for a specific RFQ (needs RFQ number, e.g., "Show quotations for RFQ-000039")
    - GET_QUOTATION_DETAILS: User wants details of a specific quotation (needs QT number, e.g., "Show QT-000030")
    - COMPARE_QUOTATIONS: User wants to compare quotations (needs RFQ number, e.g., "Compare quotations for RFQ-000039")
    - APPROVE_QUOTATION: User wants to approve a quotation (needs QT number, e.g., "Approve QT-000030")
    - REJECT_QUOTATION: User wants to reject a quotation (needs QT number, e.g., "Reject QT-000030")

    VENDOR OPERATIONS:
    - SEARCH_VENDORS: User wants to search or list vendors (e.g., "Search for ABC Supplies", "Show me vendors")
    - GET_VENDOR: User wants details of a specific vendor (e.g., "Get vendor details", "Show vendor ABC")

    PROCUREMENT OPERATIONS:
    - GET_PROCUREMENT_REQUESTS: User wants to list procurement requests (e.g., "Show me procurement requests", "List PRs")
    - GET_PROCUREMENT_REQUEST_DETAILS: User wants details of a specific PR (needs PR number, e.g., "Show PR-000001")

    APPROVAL OPERATIONS:
    - GET_APPROVALS: User wants to list pending approvals (e.g., "Show pending approvals")

    KNOWLEDGE OPERATIONS:
    - KNOWLEDGE_QUERY: User is asking about procurement concepts, definitions, or processes (e.g., "What is procurement?", "Explain RFQ process")
    - HELP: User is asking for help or available commands (e.g., "Help", "What can you do?")

    OTHER:
    - FOLLOW_UP: User is asking a follow-up question (e.g., "Show it", "Tell me more")
    - UNKNOWN: If none of the above match

    Also extract any entities:
    - rfq_number: RFQ-000039, RFQ 000039, 39
    - quotation_id: 30, QT-000030
    - quotation_number: QT-000030
    - vendor_search: "ABC Supplies" (search term)
    - vendor_id: 54
    - pr_number: PR-000001, 1

    Return ONLY valid JSON with this structure:
    {
        "operation": "OPERATION_NAME",
        "entities": {
            "rfq_number": "RFQ-000039",
            "quotation_id": 30,
            "quotation_number": "QT-000030",
            "vendor_search": "ABC Supplies",
            "vendor_id": 54,
            "pr_number": "PR-000001"
        },
        "confidence": 0.95,
        "reason": "Brief explanation of classification"
    }

    IMPORTANT:
    - confidence should be between 0.0 and 1.0
    - Only include entity fields that are present in the query
    - For list queries (GET_RFQS, GET_QUOTATIONS, etc.), don't extract entities unless specifically mentioned
    """

    # ============================================================
    # FOLLOW-UP PATTERNS (Regex fallback for simple cases)
    # ============================================================

    FOLLOW_UP_QUERIES = {
        "show it", "show that", "tell me more", "what about it", 
        "more details", "go on", "continue", "about that", 
        "regarding that", "elaborate", "explain more",
        "what else", "anything else", "further", "additional",
        "and that", "that's it", "that is it"
    }

    FOLLOW_UP_PATTERN = re.compile(
        r'^(show it|show that|tell me more|what about it|more details|go on|continue|'
        r'and\s+that|about\s+that|regarding\s+that|elaborate|explain\s+more|'
        r'what\s+else|anything\s+else|further|additional)',
        re.IGNORECASE
    )

    # ============================================================
    # MAIN RESOLVE METHOD
    # ============================================================

    @classmethod
    def resolve(cls, user_query: str, previous_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Resolve operation using LLM with structured output.
        """
        query = user_query.strip()
        previous_context = previous_context or {}
        
        # ============================================================
        # 1. CHECK FOLLOW-UP FIRST (Regex - fast path)
        # ============================================================
        
        if query.lower() in cls.FOLLOW_UP_QUERIES or cls.FOLLOW_UP_PATTERN.search(query.lower()):
            previous_op = previous_context.get("last_operation")
            if previous_op and previous_op != OperationType.UNKNOWN:
                return {
                    "operation": previous_op,
                    "entities": previous_context.get("entities", {}),
                    "confidence": 0.90,
                    "is_follow_up": True,
                    "reason": "Follow-up to previous query"
                }
            
            return {
                "operation": OperationType.UNKNOWN,
                "entities": {},
                "confidence": 0.0,
                "is_follow_up": True,
                "reason": "Follow-up with no prior context"
            }
        
        # ============================================================
        # 2. LLM-BASED CLASSIFICATION
        # ============================================================
        
        # Build context
        context_str = ""
        if previous_context:
            context_parts = []
            if previous_context.get("active_rfq"):
                context_parts.append(f"Active RFQ: {previous_context['active_rfq']}")
            if previous_context.get("active_quotation"):
                context_parts.append(f"Active Quotation: {previous_context['active_quotation']}")
            if previous_context.get("last_operation"):
                context_parts.append(f"Last operation: {previous_context['last_operation']}")
            if previous_context.get("last_intent"):
                context_parts.append(f"Last intent: {previous_context['last_intent']}")
            if context_parts:
                context_str = "Previous conversation context:\n" + "\n".join(context_parts) + "\n\n"
        
        # Build the prompt
        system_prompt = cls.SYSTEM_PROMPT
        
        user_message = f"""
{context_str}
User query: {query}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            llm = get_llm()
            
            # Use structured output with JSON mode
            structured_llm = llm.with_structured_output(
                method="json_mode",
                include_raw=False
            )
            
            response = structured_llm.invoke(messages)
            
            # Parse the response
            if isinstance(response, dict):
                operation = response.get("operation", OperationType.UNKNOWN)
                entities = response.get("entities", {})
                confidence = response.get("confidence", 0.5)
                reason = response.get("reason", "")
                
                logger.info(f"LLM resolved: {operation} (confidence: {confidence})")
                logger.info(f"Entities: {entities}")
                logger.info(f"Reason: {reason}")
                
                return {
                    "operation": operation,
                    "entities": entities,
                    "confidence": confidence,
                    "is_follow_up": False,
                    "reason": reason
                }
            
            # If response is not a dict, try to parse as JSON
            if hasattr(response, 'content'):
                content = response.content
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        "operation": result.get("operation", OperationType.UNKNOWN),
                        "entities": result.get("entities", {}),
                        "confidence": result.get("confidence", 0.5),
                        "is_follow_up": False,
                        "reason": result.get("reason", "")
                    }
            
        except Exception as e:
            logger.error(f"LLM resolution failed: {e}")
        
        # ============================================================
        # 3. FALLBACK: Use regex as fallback
        # ============================================================
        
        logger.warning("LLM resolution failed, using regex fallback")
        return cls._resolve_with_regex_fallback(query, previous_context)
    
    # ============================================================
    # REGEX FALLBACK
    # ============================================================

    @staticmethod
    def _resolve_with_regex_fallback(query: str, previous_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Regex fallback when LLM fails."""
        query_lower = query.lower()
        result = {
            "operation": OperationType.UNKNOWN,
            "entities": {},
            "confidence": 0.0,
            "is_follow_up": False,
            "reason": "Regex fallback"
        }
        
        # Simple keyword-based detection
        if "rfq" in query_lower:
            if "status" in query_lower:
                result["operation"] = OperationType.GET_RFQ_STATUS
                result["confidence"] = 0.70
            elif "show" in query_lower or "detail" in query_lower:
                result["operation"] = OperationType.GET_RFQ_DETAILS
                result["confidence"] = 0.70
            else:
                result["operation"] = OperationType.GET_RFQS
                result["confidence"] = 0.65
            return result
        
        if "quotation" in query_lower or "quote" in query_lower:
            if "approve" in query_lower:
                result["operation"] = OperationType.APPROVE_QUOTATION
                result["confidence"] = 0.70
            elif "reject" in query_lower:
                result["operation"] = OperationType.REJECT_QUOTATION
                result["confidence"] = 0.70
            elif "compare" in query_lower:
                result["operation"] = OperationType.COMPARE_QUOTATIONS
                result["confidence"] = 0.70
            else:
                result["operation"] = OperationType.GET_QUOTATIONS
                result["confidence"] = 0.65
            return result
        
        if "vendor" in query_lower:
            if "detail" in query_lower or "show" in query_lower:
                result["operation"] = OperationType.GET_VENDOR
                result["confidence"] = 0.70
            else:
                result["operation"] = OperationType.SEARCH_VENDORS
                result["confidence"] = 0.65
            return result
        
        if "procurement" in query_lower or "purchase" in query_lower:
            result["operation"] = OperationType.GET_PROCUREMENT_REQUESTS
            result["confidence"] = 0.65
            return result
        
        if "approval" in query_lower:
            result["operation"] = OperationType.GET_APPROVALS
            result["confidence"] = 0.65
            return result
        
        return result


def get_operation_description(operation: str) -> str:
    """Get human-readable description of an operation."""
    descriptions = {
        OperationType.GET_RFQS: "List all RFQs",
        OperationType.GET_RFQ_DETAILS: "Get RFQ details",
        OperationType.GET_RFQ_STATUS: "Get RFQ status",
        OperationType.GET_QUOTATIONS: "List all quotations",
        OperationType.GET_RFQ_QUOTATIONS: "Get quotations for RFQ",
        OperationType.GET_QUOTATION_DETAILS: "Get quotation details",
        OperationType.COMPARE_QUOTATIONS: "Compare quotations",
        OperationType.APPROVE_QUOTATION: "Approve quotation",
        OperationType.REJECT_QUOTATION: "Reject quotation",
        OperationType.SEARCH_VENDORS: "Search vendors",
        OperationType.GET_VENDOR: "Get vendor details",
        OperationType.GET_PROCUREMENT_REQUESTS: "List procurement requests",
        OperationType.GET_PROCUREMENT_REQUEST_DETAILS: "Get PR details",
        OperationType.GET_APPROVALS: "List pending approvals",
        OperationType.KNOWLEDGE_QUERY: "Knowledge/definition query",
        OperationType.HELP: "Show help",
        OperationType.FOLLOW_UP: "Follow-up query",
        OperationType.UNKNOWN: "Unknown operation",
    }
    return descriptions.get(operation, "Unknown operation")