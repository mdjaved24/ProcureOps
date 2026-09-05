from typing import Any

from app.ai.agents.state import ProcureOpsState
from app.ai.mcp.tools.action_service import ActionMCPService
from app.ai.services.agent_authorization_service import AgentAuthorizationService
from app.core.database import SessionLocal


def action_execution_node(
    state: ProcureOpsState,
) -> dict[str, Any]:

    operation = state.get("operation")
    quotation_id = state.get("quotation_id")
    user_id = state.get("user_id")
    hitl_decision = state.get("hitl_decision")

    # ==========================================
    # VALIDATE ACTION
    # ==========================================

    if operation not in {
        "APPROVE_QUOTATION",
        "REJECT_QUOTATION",
    }:
        return {
            "hitl_result": {
                "success": False,
                "message": "Unsupported action.",
            }
        }

    # ==========================================
    # HUMAN APPROVAL REQUIRED
    # ==========================================

    if hitl_decision != "APPROVE":
        return {
            "hitl_result": {
                "success": False,
                "message": (
                    "Action was not approved by the human."
                ),
            }
        }

    # ==========================================
    # VALIDATE INPUT
    # ==========================================

    if quotation_id is None:
        return {
            "hitl_result": {
                "success": False,
                "message": "Quotation ID is required.",
            }
        }

    if user_id is None:
        return {
            "hitl_result": {
                "success": False,
                "message": "User ID is required.",
            }
        }

    # ==========================================
    # EXECUTE ACTION
    # ==========================================

    db = SessionLocal()

    try:
        # Get user for authorization
        current_user = AgentAuthorizationService.get_user(
            db=db,
            user_id=user_id,
        )

        if current_user is None:
            return {
                "hitl_result": {
                    "success": False,
                    "message": "User not found.",
                }
            }

        if not current_user.is_active:
            return {
                "hitl_result": {
                    "success": False,
                    "message": "User account is inactive.",
                }
            }

        # Execute the action
        if operation == "APPROVE_QUOTATION":
            result = ActionMCPService.approve_quotation(
                db=db,
                quotation_id=quotation_id,
            )
        else:
            result = ActionMCPService.reject_quotation(
                db=db,
                quotation_id=quotation_id,
            )

        return {
            "hitl_result": result,
        }

    finally:
        db.close()