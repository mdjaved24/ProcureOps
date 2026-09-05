from app.ai.agents.state import ProcureOpsState

def data_access_router(
    state:ProcureOpsState,
)->str:

    data_access_type = state.get("data_access_type")

    if data_access_type == "KNOWLEDGE":
        return "rag"

    if data_access_type == "LIVE_DATA":
        return "live_data"

    return "general"
