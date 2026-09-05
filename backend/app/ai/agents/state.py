from typing import Any, Optional, List, Dict
from typing_extensions import TypedDict


class ConversationContext(TypedDict, total=False):
    """Conversation context for maintaining state across turns."""
    active_rfq: Optional[str]
    active_vendor: Optional[str]
    active_purchase_request: Optional[str]
    active_quotation: Optional[str]
    last_result: Optional[Dict[str, Any]]
    referenced_entities: List[Dict[str, Any]]
    cheapest_vendor: Optional[Dict[str, Any]]
    last_operation: Optional[str]
    last_intent: Optional[str]
    entities: Optional[Dict[str, Any]]


class ProcureOpsState(TypedDict, total=False):
    # ============================================================
    # User / Conversation Identity
    # ============================================================
    user_id: Optional[int]
    user_query: str

    # ============================================================
    # Operation Resolution (LLM-based)
    # ============================================================
    operation: Optional[str]
    intent: Optional[str]
    confidence: Optional[float]
    last_operation: Optional[str]
    last_intent: Optional[str]
    is_follow_up: Optional[bool]
    entities: Optional[Dict[str, Any]]

    # ============================================================
    # Conversation Context
    # ============================================================
    conversation_context: ConversationContext

    # ============================================================
    # Entity Extraction - RFQ
    # ============================================================
    rfq_number: Optional[str]
    rfq_id: Optional[int]

    # ============================================================
    # Entity Extraction - Vendor
    # ============================================================
    vendor_id: Optional[int]
    vendor_code: Optional[str]
    vendor_name: Optional[str]
    vendor_search: Optional[str]
    vendor_status: Optional[str]
    vendor_limit: Optional[int]

    # ============================================================
    # Entity Extraction - Purchase Request
    # ============================================================
    purchase_request_number: Optional[str]
    purchase_request_id: Optional[int]

    # ============================================================
    # Entity Extraction - Quotation
    # ============================================================
    quotation_number: Optional[str]
    quotation_id: Optional[int]

    # ============================================================
    # Data Access
    # ============================================================
    data_access_type: Optional[str]  # "LIVE_DATA", "KNOWLEDGE", "GENERAL"
    data_access_confidence: Optional[float]

    # ============================================================
    # Live Data Results
    # ============================================================
    live_data: Optional[Dict[str, Any]]
    sources: Optional[List[Dict[str, Any]]]

    # ============================================================
    # Response
    # ============================================================
    response: Optional[str]
    error: Optional[str]

    # ============================================================
    # Memory
    # ============================================================
    long_term_memory: Optional[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]

    # ============================================================
    # HITL (Human-in-the-Loop)
    # ============================================================
    hitl_required: Optional[bool]
    hitl_action: Optional[str]
    hitl_status: Optional[str]
    hitl_request: Optional[Dict[str, Any]]
    hitl_decision: Optional[str]
    hitl_result: Optional[Dict[str, Any]]

    # ============================================================
    # Guardrails
    # ============================================================
    guardrail_allowed: Optional[bool]
    guardrail_category: Optional[str]