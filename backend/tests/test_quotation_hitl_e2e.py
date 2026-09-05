from unittest.mock import patch

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.ai.agents.nodes.action_execution_node import action_execution_node
from app.ai.agents.nodes.context_resolution_node import context_resolution_node
from app.ai.agents.nodes.hitl_node import hitl_node
from app.ai.agents.nodes.operation_resolution_node import operation_resolution_node
from app.ai.agents.state import ProcureOpsState
from app.core.database import SessionLocal
from app.models.quotation.quotation import Quotation


def build_test_graph():

    workflow = StateGraph(ProcureOpsState)

    workflow.add_node(
        "context_resolution",
        context_resolution_node,
    )

    workflow.add_node(
        "operation_resolution",
        operation_resolution_node,
    )

    workflow.add_node(
        "hitl",
        hitl_node,
    )

    workflow.add_node(
        "action_execution",
        action_execution_node,
    )

    workflow.add_edge(
        START,
        "context_resolution",
    )

    workflow.add_edge(
        "context_resolution",
        "operation_resolution",
    )

    workflow.add_edge(
        "operation_resolution",
        "hitl",
    )

    workflow.add_conditional_edges(
        "hitl",
        lambda state: "action_execution",
        {
            "action_execution": "action_execution",
        },
    )

    workflow.add_edge(
        "action_execution",
        END,
    )

    return workflow.compile(
        checkpointer=MemorySaver()
    )


def test_real_quotation_approval_e2e():

    quotation_id = 1

    # Verify real DB state before test
    db = SessionLocal()

    try:
        quotation = db.get(
            Quotation,
            quotation_id,
        )

        assert quotation is not None
        assert quotation.status == "SUBMITTED"

    finally:
        db.close()

    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "real-quotation-approval-001",
        }
    }

    initial_state = {
        "user_id": 101,
        "user_query": "Approve quotation QT-000001",
    }

    fake_user = type(
        "FakeUser",
        (),
        {
            "id": 101,
            "is_active": True,
        },
    )()

    fake_quotation = type(
        "FakeQuotation",
        (),
        {
            "id": 1,
            "quotation_number": "QT-000001",
            "status": "SUBMITTED",
        },
    )()

    # ------------------------------------------
    # First invocation → HITL pause
    # ------------------------------------------

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=fake_user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=fake_quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        paused = graph.invoke(
            initial_state,
            config=config,
        )

    assert "__interrupt__" in paused

    interrupt_value = paused["__interrupt__"][0].value

    assert (
        interrupt_value["action"]
        == "APPROVE_QUOTATION"
    )

    assert (
        interrupt_value["quotation_number"]
        == "QT-000001"
    )

    # ------------------------------------------
    # Resume → Human approves
    # ------------------------------------------

    with patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.get_user",
        return_value=fake_user,
    ), patch(
        "app.ai.agents.nodes.hitl_node.AgentAuthorizationService.has_permission",
        return_value=True,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.get_quotation",
        return_value=fake_quotation,
    ), patch(
        "app.ai.agents.nodes.hitl_node.QuotationAuthorizationService.validate_action",
        return_value=(True, ""),
    ):

        result = graph.invoke(
            Command(
                resume={
                    "decision": "APPROVE",
                }
            ),
            config=config,
        )

    assert result["hitl_decision"] == "APPROVE"

    assert result["hitl_result"]["success"] is True

    # ------------------------------------------
    # Verify REAL PostgreSQL state
    # ------------------------------------------

    db = SessionLocal()

    try:
        quotation = db.get(
            Quotation,
            quotation_id,
        )

        assert quotation.status == "ACCEPTED"

    finally:
        db.close()