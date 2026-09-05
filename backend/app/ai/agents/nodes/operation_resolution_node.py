from typing import Dict, Any
import logging

from app.ai.agents.state import ProcureOpsState
from app.ai.services.operation_resolver import (
    OperationResolver, 
    OperationType, 
    get_operation_description
)

logger = logging.getLogger(__name__)


def operation_resolution_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Resolve the user's query to a specific operation using LLM.
    """
    user_query = state.get("user_query", "")
    previous_context = state.get("conversation_context", {})
    
    logger.info(f"Resolving operation for: '{user_query}'")
    
    # Resolve operation using LLM
    result = OperationResolver.resolve(user_query, previous_context)
    
    operation = result.get("operation")
    entities = result.get("entities", {})
    confidence = result.get("confidence", 0.0)
    is_follow_up = result.get("is_follow_up", False)
    reason = result.get("reason", "")
    
    logger.info(f"Operation: {operation} (confidence: {confidence})")
    logger.info(f"Reason: {reason}")
    if entities:
        logger.info(f"Entities: {entities}")
    
    # ============================================================
    # DETERMINE DATA ACCESS TYPE
    # ============================================================
    
    # LIVE_DATA operations - require database access
    live_data_operations = {
        OperationType.GET_RFQS,
        OperationType.GET_RFQ_DETAILS,
        OperationType.GET_RFQ_STATUS,
        OperationType.GET_QUOTATIONS,
        OperationType.GET_RFQ_QUOTATIONS,
        OperationType.GET_QUOTATION_DETAILS,
        OperationType.COMPARE_QUOTATIONS,
        OperationType.APPROVE_QUOTATION,
        OperationType.REJECT_QUOTATION,
        OperationType.SEARCH_VENDORS,
        OperationType.GET_VENDOR,
        OperationType.GET_VENDOR_DETAILS,
        OperationType.GET_PROCUREMENT_REQUESTS,
        OperationType.GET_PROCUREMENT_REQUEST_DETAILS,
        OperationType.GET_APPROVALS,
    }
    
    # KNOWLEDGE operations - use RAG
    knowledge_operations = {
        OperationType.KNOWLEDGE_QUERY,
        OperationType.HELP,
    }
    
    # GENERAL operations - fallback
    general_operations = {
        OperationType.UNKNOWN,
        OperationType.FOLLOW_UP,
    }
    
    if operation in live_data_operations:
        data_access_type = "LIVE_DATA"
        data_access_confidence = confidence
    elif operation in knowledge_operations:
        data_access_type = "KNOWLEDGE"
        data_access_confidence = max(confidence, 0.85)
    else:
        data_access_type = "GENERAL"
        data_access_confidence = 0.50
    
    # ============================================================
    # BUILD RETURN STATE
    # ============================================================
    
    return_state: Dict[str, Any] = {
        "operation": operation,
        "confidence": confidence,
        "entities": entities,
        "is_follow_up": is_follow_up,
        "intent": _map_operation_to_intent(operation),
        "data_access_type": data_access_type,
        "data_access_confidence": data_access_confidence,
    }
    
    # Store entities in state
    if entities.get("rfq_number"):
        return_state["rfq_number"] = entities["rfq_number"]
    if entities.get("rfq_id"):
        return_state["rfq_id"] = entities["rfq_id"]
    if entities.get("quotation_id"):
        return_state["quotation_id"] = entities["quotation_id"]
    if entities.get("quotation_number"):
        return_state["quotation_number"] = entities["quotation_number"]
    if entities.get("vendor_search"):
        return_state["vendor_search"] = entities["vendor_search"]
    if entities.get("vendor_id"):
        return_state["vendor_id"] = entities["vendor_id"]
    if entities.get("pr_number"):
        return_state["purchase_request_number"] = entities["pr_number"]
    if entities.get("pr_id"):
        return_state["purchase_request_id"] = entities["pr_id"]
    
    # Store last operation
    if operation and operation != OperationType.UNKNOWN:
        return_state["last_operation"] = operation
        return_state["last_intent"] = return_state["intent"]
        return_state["conversation_context"] = {
            **previous_context,
            "last_operation": operation,
            "last_intent": return_state["intent"],
            "entities": entities,
        }
    
    return return_state


def _map_operation_to_intent(operation: str) -> str:
    """Map operation to intent."""
    intent_map = {
        OperationType.GET_RFQS: "RFQ",
        OperationType.GET_RFQ_DETAILS: "RFQ",
        OperationType.GET_RFQ_STATUS: "RFQ",
        OperationType.GET_QUOTATIONS: "QUOTATION",
        OperationType.GET_RFQ_QUOTATIONS: "QUOTATION",
        OperationType.GET_QUOTATION_DETAILS: "QUOTATION",
        OperationType.COMPARE_QUOTATIONS: "QUOTATION",
        OperationType.APPROVE_QUOTATION: "QUOTATION",
        OperationType.REJECT_QUOTATION: "QUOTATION",
        OperationType.SEARCH_VENDORS: "VENDOR",
        OperationType.GET_VENDOR: "VENDOR",
        OperationType.GET_VENDOR_DETAILS: "VENDOR",
        OperationType.GET_PROCUREMENT_REQUESTS: "PURCHASE_REQUEST",
        OperationType.GET_PROCUREMENT_REQUEST_DETAILS: "PURCHASE_REQUEST",
        OperationType.GET_APPROVALS: "APPROVAL",
        OperationType.KNOWLEDGE_QUERY: "KNOWLEDGE",
        OperationType.HELP: "HELP",
        OperationType.FOLLOW_UP: "FOLLOW_UP",
    }
    return intent_map.get(operation, "UNKNOWN")