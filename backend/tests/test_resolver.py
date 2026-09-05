
import pytest

from app.ai.agents.nodes.context_resolution_node import (
    context_resolution_node,
)


# ============================================================
# TEST 1: EXPLICIT RFQ IN CURRENT QUERY
# ============================================================

def test_context_resolution_with_explicit_rfq():

    state = {
        "user_query": "Compare quotations for RFQ-000013",

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"

    assert (
        result["conversation_context"]["active_rfq"]
        == "RFQ-000013"
    )


# ============================================================
# TEST 2: EXPLICIT RFQ SHOULD UPDATE EXISTING CONTEXT
# ============================================================

def test_explicit_rfq_replaces_previous_active_rfq():

    state = {
        "user_query": "Show quotations for RFQ-000999",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
        },
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000999"

    assert (
        result["conversation_context"]["active_rfq"]
        == "RFQ-000999"
    )


# ============================================================
# TEST 3: REUSE ACTIVE RFQ FROM CONVERSATION CONTEXT
# ============================================================

def test_context_resolution_uses_active_rfq():

    state = {
        "user_query": "Show quotations",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
        },
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"

    # No need to modify conversation context because
    # the active RFQ is already present.
    assert "conversation_context" not in result


# ============================================================
# TEST 4: EMPTY QUERY CONTEXT
# ============================================================

def test_context_resolution_without_rfq_context():

    state = {
        "user_query": "Show quotations",

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result == {}


# ============================================================
# TEST 5: NO conversation_context KEY
# ============================================================

def test_context_resolution_without_conversation_context():

    state = {
        "user_query": "Show quotations",
    }

    result = context_resolution_node(state)

    assert result == {}


# ============================================================
# TEST 6: BACKWARD COMPATIBILITY WITH rfq_number
# ============================================================

def test_context_resolution_uses_legacy_rfq_number():

    state = {
        "user_query": "Show quotations",

        "rfq_number": "RFQ-000013",

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"


# ============================================================
# TEST 7: EXPLICIT RFQ TAKES PRIORITY OVER OLD STATE
# ============================================================

def test_explicit_rfq_has_priority_over_previous_state():

    state = {
        "user_query": "Compare quotations for RFQ-000999",

        "rfq_number": "RFQ-000013",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
        },
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000999"

    assert (
        result["conversation_context"]["active_rfq"]
        == "RFQ-000999"
    )


# ============================================================
# TEST 8: CASE INSENSITIVE RFQ EXTRACTION
# ============================================================

@pytest.mark.parametrize(
    "query",
    [
        "Compare quotations for rfq-000013",
        "Compare quotations for RFQ-000013",
        "Compare quotations for Rfq-000013",
    ],
)
def test_rfq_extraction_is_case_insensitive(query):

    state = {
        "user_query": query,

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"


# ============================================================
# TEST 9: RFQ EMBEDDED INSIDE A NATURAL QUERY
# ============================================================

@pytest.mark.parametrize(
    "query",
    [
        "What is the status of RFQ-000013?",
        "Show me quotations submitted for RFQ-000013",
        "Compare all vendor quotations for RFQ-000013 please",
        "Give me details about RFQ-000013",
    ],
)
def test_rfq_extraction_from_natural_language(query):

    state = {
        "user_query": query,

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"


# ============================================================
# TEST 10: INVALID RFQ FORMAT SHOULD NOT MATCH
# ============================================================

@pytest.mark.parametrize(
    "query",
    [
        "Compare quotations for 000013",
        "Compare quotations for RFQ",
        "Compare quotations for RFQ-ABC",
        "Compare quotations for REQ-000013",
    ],
)
def test_invalid_rfq_format(query):

    state = {
        "user_query": query,

        "conversation_context": {},
    }

    result = context_resolution_node(state)

    assert result == {}


# ============================================================
# TEST 11: PREVIOUS RFQ IS USED ONLY WHEN CURRENT QUERY
# DOES NOT CONTAIN AN RFQ
# ============================================================

def test_previous_rfq_used_when_query_has_no_rfq():

    state = {
        "user_query": "What are the quotations?",

        "rfq_number": "RFQ-000013",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
        },
    }

    result = context_resolution_node(state)

    assert result["rfq_number"] == "RFQ-000013"


# ============================================================
# TEST 12: EXPLICIT RFQ UPDATES ONLY ACTIVE RFQ
# AND PRESERVES OTHER CONTEXT
# ============================================================

def test_explicit_rfq_preserves_existing_context():

    state = {
        "user_query": "Compare quotations for RFQ-000999",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
            "active_vendor": "VENDOR-004",
            "active_quotation": "QUO-001",
        },
    }

    result = context_resolution_node(state)

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000999"

    assert context["active_vendor"] == "VENDOR-004"

    assert context["active_quotation"] == "QUO-001"