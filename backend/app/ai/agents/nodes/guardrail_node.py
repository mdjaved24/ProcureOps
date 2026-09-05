from typing import Any, Dict

from app.ai.agents.state import ProcureOpsState
from app.ai.guardrails.guardrail_service import GuardrailService


def guardrail_node(
    state: ProcureOpsState,
) -> Dict[str, Any]:
    """
    Check if the user query passes guardrails.
    """
    user_query = state.get("user_query", "")

    result = GuardrailService.validate(
        user_query=user_query,
    )

    return {
        "guardrail_allowed": result["allowed"],
        "guardrail_category": result["category"],
        "response": (
            None
            if result["allowed"]
            else result["reason"]
        ),
    }