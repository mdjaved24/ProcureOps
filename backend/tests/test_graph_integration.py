import pytest

from app.ai.agents.graph import (
    ProcureOpsGraph,
)


# ============================================================
# TEST: GRAPH MEMORY INTEGRATION
# ============================================================

@pytest.mark.asyncio
async def test_graph_preserves_conversation_context():

    # --------------------------------------------------------
    # Build graph
    # --------------------------------------------------------

    graph = ProcureOpsGraph.build_graph()

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Every invocation using the same thread_id belongs
    # to the same conversation.
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": "test-context-resolution-001",
        }
    }

    # ========================================================
    # TURN 1
    # ========================================================

    turn_1_state = {
        "user_query": (
            "Compare quotations for RFQ-000013"
        ),
    }

    result_1 = await graph.ainvoke(
        turn_1_state,
        config=config,
    )

    # --------------------------------------------------------
    # Basic response validation
    # --------------------------------------------------------

    assert result_1 is not None

    # --------------------------------------------------------
    # RFQ should be resolved
    # --------------------------------------------------------

    assert (
        result_1.get("rfq_number")
        == "RFQ-000013"
    )

    # --------------------------------------------------------
    # Conversation context should exist
    # --------------------------------------------------------

    context_1 = result_1.get(
        "conversation_context"
    )

    assert context_1 is not None

    assert (
        context_1.get("active_rfq")
        == "RFQ-000013"
    )

    # --------------------------------------------------------
    # Comparison should have produced live data
    # --------------------------------------------------------

    assert (
        result_1.get("live_data")
        is not None
    )

    # --------------------------------------------------------
    # Cheapest vendor should exist if quotations exist.
    #
    # We don't hardcode the vendor here because that depends
    # on the actual database data.
    # --------------------------------------------------------

    live_data = result_1["live_data"]

    comparison = live_data.get(
        "comparison"
    )

    if comparison:

        quotations = comparison.get(
            "quotations",
            []
        )

        if quotations:

            assert (
                context_1.get(
                    "cheapest_vendor"
                )
                is not None
            )

    # ========================================================
    # TURN 2
    # ========================================================

    turn_2_state = {
        "user_query": (
            "Show quotations"
        ),
    }

    result_2 = await graph.ainvoke(
        turn_2_state,
        config=config,
    )

    # --------------------------------------------------------
    # The second request did NOT specify an RFQ.
    #
    # It should recover RFQ-000013 from conversation memory.
    # --------------------------------------------------------

    assert (
        result_2.get("rfq_number")
        == "RFQ-000013"
    )

    context_2 = result_2.get(
        "conversation_context"
    )

    assert context_2 is not None

    assert (
        context_2.get("active_rfq")
        == "RFQ-000013"
    )

    # ========================================================
    # TURN 3
    # ========================================================

    turn_3_state = {
        "user_query": (
            "Compare them"
        ),
    }

    result_3 = await graph.ainvoke(
        turn_3_state,
        config=config,
    )

    # --------------------------------------------------------
    # "them" should currently reuse the previous operation.
    #
    # Your OperationResolver already handles:
    #
    # "compare them"
    #       ↓
    # previous_operation
    #       ↓
    # COMPARE_QUOTATIONS
    # --------------------------------------------------------

    assert (
        result_3.get("operation")
        == "COMPARE_QUOTATIONS"
    )

    assert (
        result_3.get("rfq_number")
        == "RFQ-000013"
    )