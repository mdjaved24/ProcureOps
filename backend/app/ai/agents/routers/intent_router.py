from app.ai.agents.state import ProcureOpsState

def intent_router(
    state:ProcureOpsState,
)->str:

    intent = state.get("intent")

    # ==============================================
    # KNOWLEDGE BASE ROUTING
    # ==============================================

    rag_intents = {
        "PURCHASE_REQUEST",
        "RFQ",
        "QUOTATION",
        "VENDOR",
        "POLICY",
    }

    if intent in rag_intents:

        return "rag_node"


    # ==============================================
    # GENERAL PROCUREMENT
    # ==============================================

    if intent == "GENERAL PROCUREMENT":
        return "general_node"

    # ==============================================
    # FALLBACK
    # ==============================================

    return "general_node"
