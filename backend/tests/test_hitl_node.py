from types import SimpleNamespace
from unittest.mock import patch

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.ai.agents.nodes.hitl_node import hitl_node
from app.ai.agents.state import ProcureOpsState


# ============================================================
# TEST GRAPH
# ============================================================

def build_test_graph():
    workflow = StateGraph(ProcureOpsState)

    workflow.add_node("hitl", hitl_node)

    workflow.add_edge(START, "hitl")
    workflow.add_edge("hitl", END)

    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)


# ============================================================
# TEST FIXTURES / HELPERS
# ============================================================

def fake_user(
    user_id: int = 101,
    is_active: bool = True,
):
    return SimpleNamespace(
        id=user_id,
        is_active=is_active,
    )


def fake_quotation(
    quotation_id: int = 123,
    quotation_number: str = "QT-123",
):
    return SimpleNamespace(
        id=quotation_id,
        quotation_number=quotation_number,
    )


# ============================================================
# NON-SENSITIVE OPERATION
# ============================================================

def test_non_sensitive_operation_does_not_require_hitl():

    state = {
        "operation": "GET_QUOTATIONS",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    result = hitl_node(state)

    assert result == {
        "hitl_required": False,
    }


# ============================================================
# USER VALIDATION
# ============================================================

def test_sensitive_action_without_user_id_is_rejected():

    state = {
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"

    assert (
        "Authenticated user is required"
        in result["error"]
    )


def test_unknown_user_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=None,
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"
    assert result["error"] == "User not found."


def test_inactive_user_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user(
        user_id=101,
        is_active=False,
    )

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"
    assert result["error"] == "User account is inactive."


# ============================================================
# QUOTATION IDENTIFICATION
# ============================================================

def test_sensitive_action_without_quotation_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
    }

    result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "INVALID"

    assert (
        "Quotation information is required"
        in result["error"]
    )


# ============================================================
# ACTION PERMISSION
# ============================================================

def test_user_without_approval_permission_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=False,
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"
    assert result["hitl_action"] == "APPROVE_QUOTATION"

    assert (
        "do not have permission"
        in result["error"]
    )


def test_user_without_reject_permission_is_rejected():

    state = {
        "user_id": 101,
        "operation": "REJECT_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=False,
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"
    assert result["hitl_action"] == "REJECT_QUOTATION"

    assert (
        "do not have permission"
        in result["error"]
    )


# ============================================================
# QUOTATION LOOKUP
# ============================================================

def test_quotation_not_found_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=None,
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "INVALID"
    assert result["error"] == "Quotation not found."


# ============================================================
# QUOTATION ACTION VALIDATION
# ============================================================

def test_invalid_quotation_action_is_rejected():

    state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()
    quotation = fake_quotation()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(
            False,
            "Only submitted quotations can be acted upon.",
        ),
    ):

        result = hitl_node(state)

    assert result["hitl_required"] is False
    assert result["hitl_status"] == "UNAUTHORIZED"
    assert result["hitl_action"] == "APPROVE_QUOTATION"

    assert (
        result["error"]
        == "Only submitted quotations can be acted upon."
    )


# ============================================================
# HITL INTERRUPT
# ============================================================

def test_hitl_interrupts_before_decision():

    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "hitl-test-approve-001",
        }
    }

    initial_state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()

    quotation = fake_quotation()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        result = graph.invoke(
            initial_state,
            config=config,
        )

    assert "__interrupt__" in result

    interrupts = result["__interrupt__"]

    assert len(interrupts) == 1

    interrupt_value = interrupts[0].value

    assert (
        interrupt_value["action"]
        == "APPROVE_QUOTATION"
    )

    assert (
        interrupt_value["quotation_id"]
        == 123
    )

    assert (
        interrupt_value["quotation_number"]
        == "QT-123"
    )


# ============================================================
# HITL APPROVAL RESUME
# ============================================================

def test_hitl_resumes_with_approval_decision():

    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "hitl-test-resume-approve-001",
        }
    }

    initial_state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()

    quotation = fake_quotation()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        paused_result = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in paused_result

        resumed_result = graph.invoke(
            Command(
                resume={
                    "decision": "APPROVE",
                }
            ),
            config=config,
        )

    assert resumed_result["hitl_required"] is True

    assert (
        resumed_result["hitl_status"]
        == "APPROVE"
    )

    assert (
        resumed_result["hitl_decision"]
        == "APPROVE"
    )


# ============================================================
# HITL REJECTION RESUME
# ============================================================

def test_hitl_resumes_with_rejection_decision():

    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "hitl-test-resume-reject-001",
        }
    }

    initial_state = {
        "user_id": 101,
        "operation": "REJECT_QUOTATION",
        "quotation_id": 456,
        "quotation_number": "QT-456",
    }

    user = fake_user()

    quotation = fake_quotation(
        quotation_id=456,
        quotation_number="QT-456",
    )

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        paused_result = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in paused_result

        resumed_result = graph.invoke(
            Command(
                resume={
                    "decision": "REJECT",
                }
            ),
            config=config,
        )

    assert resumed_result["hitl_required"] is True

    assert (
        resumed_result["hitl_status"]
        == "REJECT"
    )

    assert (
        resumed_result["hitl_decision"]
        == "REJECT"
    )


# ============================================================
# INVALID HUMAN DECISION
# ============================================================

def test_hitl_rejects_invalid_human_decision():

    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "hitl-test-invalid-decision-001",
        }
    }

    initial_state = {
        "user_id": 101,
        "operation": "APPROVE_QUOTATION",
        "quotation_id": 123,
        "quotation_number": "QT-123",
    }

    user = fake_user()
    quotation = fake_quotation()

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        paused_result = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in paused_result

        resumed_result = graph.invoke(
            Command(
                resume={
                    "decision": "MAYBE",
                }
            ),
            config=config,
        )

    assert resumed_result["hitl_required"] is True
    assert resumed_result["hitl_status"] == "INVALID"
    assert resumed_result["hitl_decision"] == "MAYBE"

    assert (
        "Expected APPROVE or REJECT"
        in resumed_result["error"]
    )