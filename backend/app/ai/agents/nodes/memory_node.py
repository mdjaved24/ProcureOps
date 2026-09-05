from typing import Dict, Any
import logging

from app.ai.agents.state import ProcureOpsState

logger = logging.getLogger(__name__)


async def memory_retrieval_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Retrieve long-term memory for the user.
    """
    user_id = state.get("user_id")
    
    if user_id is None:
        return {"retrieved_memories": []}
    
    try:
        # Simple in-memory cache for now
        return {"retrieved_memories": []}
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        return {"retrieved_memories": []}


def memory_update_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Update memory with current conversation context.
    """
    user_id = state.get("user_id")
    operation = state.get("last_operation")
    intent = state.get("last_intent")
    entities = state.get("entities", {})
    conversation_context = state.get("conversation_context", {})
    
    if user_id is None:
        return {}
    
    # Update conversation context
    updated_context = {
        **conversation_context,
        "last_operation": operation,
        "last_intent": intent,
        "entities": entities,
    }
    
    # Add active entities
    if entities.get("rfq_number"):
        updated_context["active_rfq"] = entities["rfq_number"]
    if entities.get("quotation_number"):
        updated_context["active_quotation"] = entities["quotation_number"]
    if entities.get("vendor_search"):
        updated_context["active_vendor"] = entities["vendor_search"]
    
    return {
        "conversation_context": updated_context,
    }