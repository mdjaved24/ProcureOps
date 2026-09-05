from typing import Dict, Any
import logging

from app.ai.agents.state import ProcureOpsState
from app.ai.services.operation_resolver import OperationType

logger = logging.getLogger(__name__)


def router_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Router node that determines the data access type and routes accordingly.
    Supports: LIVE_DATA, KNOWLEDGE, GENERAL
    """
    data_access_type = state.get("data_access_type", "GENERAL")
    operation = state.get("operation")
    intent = state.get("intent")
    
    logger.info(f"Router Node: data_access_type = {data_access_type}, operation = {operation}")
    
    # ============================================================
    # ROUTING LOGIC
    # ============================================================
    
    # 1. If operation is explicitly KNOWLEDGE_QUERY or HELP, route to RAG
    if operation in [OperationType.KNOWLEDGE_QUERY, OperationType.HELP]:
        logger.info("Routing to RAG (KNOWLEDGE_QUERY/HELP)")
        return {"data_access_type": "KNOWLEDGE"}
    
    # 2. If data_access_type is already set, use it
    if data_access_type == "KNOWLEDGE":
        logger.info("Routing to RAG (KNOWLEDGE)")
        return {}
    
    if data_access_type == "LIVE_DATA":
        logger.info("Routing to LIVE_DATA")
        return {}
    
    # 3. If data_access_type is GENERAL, try to determine the best route
    if data_access_type == "GENERAL":
        # Check if it might be a knowledge query based on intent
        if intent in ["KNOWLEDGE", "HELP"]:
            logger.info("Routing to RAG (GENERAL with knowledge intent)")
            return {"data_access_type": "KNOWLEDGE"}
        
        # Check if it has any entities that suggest LIVE_DATA
        has_entity = any([
            state.get("rfq_number"),
            state.get("quotation_id"),
            state.get("vendor_id"),
            state.get("purchase_request_number"),
        ])
        
        if has_entity:
            logger.info("Routing to LIVE_DATA (GENERAL with entities)")
            return {"data_access_type": "LIVE_DATA"}
        
        # Default to GENERAL for fallback
        logger.info("Routing to GENERAL (fallback)")
        return {"data_access_type": "GENERAL"}
    
    # 4. Default fallback
    logger.info(f"Router: No specific routing, using {data_access_type}")
    return {}