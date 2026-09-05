from typing import Any

from langgraph.types import interrupt

from app.ai.agents.state import ProcureOpsState
from app.ai.services.agent_authorization_service import (
    AgentAuthorizationService,
)
from app.ai.services.quotation_authorization_service import (
    QuotationAuthorizationService,
)

from app.core.database import SessionLocal


SENSITIVE_ACTIONS = {
    "APPROVE_QUOTATION",
    "REJECT_QUOTATION",
}


def hitl_node(
    state: ProcureOpsState,
) -> dict[str, Any]:

    operation = state.get("operation")

    # ==========================================
    # NON-SENSITIVE OPERATION
    # ==========================================

    if operation not in SENSITIVE_ACTIONS:
        return {
            "hitl_required": False,
        }

    # ==========================================
    # USER VALIDATION
    # ==========================================

    user_id = state.get("user_id")

    if user_id is None:
        return {
            "hitl_required": False,
            "hitl_status": "UNAUTHORIZED",
            "error": (
                "Authenticated user is required "
                "for this action."
            ),
        }

    # ==========================================
    # QUOTATION IDENTIFICATION
    # ==========================================

    quotation_id = state.get("quotation_id")
    quotation_number = state.get("quotation_number")

    if quotation_id is None and quotation_number is None:
        return {
            "hitl_required": False,
            "hitl_status": "INVALID",
            "error": (
                "Quotation information is required "
                "for this action."
            ),
        }

    # ==========================================
    # AUTHORIZATION + QUOTATION VALIDATION
    # ==========================================

    db = SessionLocal()

    try:
        # ------------------------------------------
        # Get authenticated user
        # ------------------------------------------

        user = AgentAuthorizationService.get_user(
            db=db,
            user_id=user_id,
        )

        if user is None:
            return {
                "hitl_required": False,
                "hitl_status": "UNAUTHORIZED",
                "error": "User not found.",
            }

        if not user.is_active:
            return {
                "hitl_required": False,
                "hitl_status": "UNAUTHORIZED",
                "error": "User account is inactive.",
            }

        # ------------------------------------------
        # Check action permission
        # ------------------------------------------

        if not AgentAuthorizationService.has_permission(
            user=user,
            action=operation,
        ):
            return {
                "hitl_required": False,
                "hitl_status": "UNAUTHORIZED",
                "hitl_action": operation,
                "error": (
                    f"You do not have permission "
                    f"to {operation.replace('_', ' ').lower()} "
                    f"quotations."
                ),
            }

        # ------------------------------------------
        # Resolve quotation
        # ------------------------------------------

        quotation = (
            QuotationAuthorizationService.get_quotation(
                db=db,
                quotation_id=quotation_id,
                quotation_number=quotation_number,
            )
        )

        if quotation is None:
            return {
                "hitl_required": False,
                "hitl_status": "INVALID",
                "error": "Quotation not found.",
            }

        # ------------------------------------------
        # Validate quotation resource/action
        # ------------------------------------------

        allowed, message = (
            QuotationAuthorizationService.validate_action(
                db=db,
                user=user,
                quotation=quotation,
                action=operation,
            )
        )

        if not allowed:
            return {
                "hitl_required": False,
                "hitl_status": "UNAUTHORIZED",
                "hitl_action": operation,
                "error": message,
            }

        # ------------------------------------------
        # Use canonical DB values
        # ------------------------------------------

        quotation_id = quotation.id
        quotation_number = quotation.quotation_number

    finally:
        db.close()

    # ==========================================
    # HITL REQUEST
    # ==========================================

    hitl_request = {
        "action": operation,
        "quotation_id": quotation_id,
        "quotation_number": quotation_number,
        "message": (
            f"Human approval is required to "
            f"{operation.replace('_', ' ').lower()} "
            f"the quotation."
        ),
        "user": {
            "id": user_id,
            "role": user.role.name if user.role else None,
        },
    }

    # ==========================================
    # PAUSE GRAPH
    # ==========================================

    decision = interrupt(hitl_request)

    # ==========================================
    # VALIDATE HUMAN DECISION
    # ==========================================

    if not isinstance(decision, dict):
        return {
            "hitl_required": True,
            "hitl_status": "INVALID",
            "hitl_request": hitl_request,
            "error": "Invalid HITL decision.",
        }

    decision_value = decision.get("decision")

    if decision_value not in {
        "APPROVE",
        "REJECT",
    }:
        return {
            "hitl_required": True,
            "hitl_status": "INVALID",
            "hitl_request": hitl_request,
            "hitl_decision": decision_value,
            "error": (
                "Invalid HITL decision. "
                "Expected APPROVE or REJECT."
            ),
        }

    # ==========================================
    # RETURN DECISION
    # ==========================================

    return {
        "hitl_required": True,
        "hitl_status": decision_value,
        "hitl_request": hitl_request,
        "hitl_decision": decision_value,
        "quotation_id": quotation_id,
        "quotation_number": quotation_number,
    }