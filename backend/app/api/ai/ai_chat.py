from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai.agents.agent_service import ProcureOpsAgentService
from app.core.dependencies import get_current_user
from app.models.identity.user import User


ai_router = APIRouter(
    prefix="/AI",
    tags=["AI"],
)


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class ChatRequest(BaseModel):

    user_query: str = Field(
        min_length=1,
        max_length=5000,
    )

    conversation_id: str = Field(
        min_length=1,
        max_length=255,
    )


class DecisionRequest(BaseModel):

    conversation_id: str = Field(
        min_length=1,
        max_length=255,
    )

    decision: str


# ============================================================
# CHAT
# ============================================================

@ai_router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):

    result = await ProcureOpsAgentService.process_query(
        user_query=request.user_query,
        conversation_id=request.conversation_id,
        user_id=current_user.id,
    )

    # --------------------------------------------------------
    # HITL INTERRUPT
    # --------------------------------------------------------

    if "__interrupt__" in result:

        interrupt = result["__interrupt__"][0]

        return {
            "status": "awaiting_approval",
            "conversation_id": request.conversation_id,
            "hitl_request": interrupt.value,
        }

    # --------------------------------------------------------
    # NORMAL RESPONSE
    # --------------------------------------------------------

    return {
        "status": "completed",
        "conversation_id": request.conversation_id,
        "response": result.get("response"),
        "sources": result.get("sources"),
        "hitl_result": result.get("hitl_result"),
    }


# ============================================================
# HITL DECISION
# ============================================================

@ai_router.post("/decision")
async def decision(
    request: DecisionRequest,
    current_user: User = Depends(get_current_user),
):

    result = await ProcureOpsAgentService.resume_query(
        conversation_id=request.conversation_id,
        decision=request.decision,
        user_id=current_user.id,
    )

    # --------------------------------------------------------
    # STILL WAITING
    # --------------------------------------------------------

    if "__interrupt__" in result:

        interrupt = result["__interrupt__"][0]

        return {
            "status": "awaiting_approval",
            "conversation_id": request.conversation_id,
            "hitl_request": interrupt.value,
        }

    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    return {
        "status": "completed",
        "conversation_id": request.conversation_id,
        "response": result.get("response"),
        "hitl_result": result.get("hitl_result"),
    }