from app.ai.agents.nodes.memory_update_node import (
    memory_update_node,
)


# ============================================================
# TEST 1
# Operation and intent memory
# ============================================================

def test_memory_update_operation_and_intent():

    state = {
        "user_query": "Compare quotations",
        "operation": "COMPARE_QUOTATIONS",
        "intent": "QUOTATION",
    }

    result = memory_update_node(state)

    assert result["last_operation"] == "COMPARE_QUOTATIONS"

    assert result["last_intent"] == "QUOTATION"


# ============================================================
# TEST 2
# Active RFQ
# ============================================================

def test_memory_update_active_rfq():

    state = {
        "user_query": "Compare quotations for RFQ-000013",

        "rfq_number": "RFQ-000013",
    }

    result = memory_update_node(state)

    assert (
        result["conversation_context"]["active_rfq"]
        == "RFQ-000013"
    )


# ============================================================
# TEST 3
# Active vendor
# ============================================================

def test_memory_update_active_vendor():

    state = {
        "user_query": "Show vendor details",

        "vendor_id": "VENDOR-004",
    }

    result = memory_update_node(state)

    assert (
        result["conversation_context"]["active_vendor"]
        == "VENDOR-004"
    )


# ============================================================
# TEST 4
# Active quotation
# ============================================================

def test_memory_update_active_quotation():

    state = {
        "user_query": "Show quotation",

        "quotation_id": "QUO-019",
    }

    result = memory_update_node(state)

    assert (
        result["conversation_context"]["active_quotation"]
        == "QUO-019"
    )


# ============================================================
# TEST 5
# Preserve existing context
# ============================================================

def test_memory_update_preserves_existing_context():

    state = {
        "user_query": "Show quotation",

        "rfq_number": "RFQ-000013",

        "conversation_context": {
            "active_vendor": "VENDOR-004",
            "active_quotation": "QUO-019",
        },
    }

    result = memory_update_node(state)

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000013"

    assert context["active_vendor"] == "VENDOR-004"

    assert context["active_quotation"] == "QUO-019"


# ============================================================
# TEST 6
# Existing context should survive when current state
# does not contain an entity
# ============================================================

def test_existing_context_survives():

    state = {
        "user_query": "Show quotations",

        "conversation_context": {
            "active_rfq": "RFQ-000013",
            "active_vendor": "VENDOR-004",
        },
    }

    result = memory_update_node(state)

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000013"

    assert context["active_vendor"] == "VENDOR-004"


# ============================================================
# TEST 7
# All entities together
# ============================================================

def test_memory_update_all_entities():

    state = {
        "user_query": "Compare quotations",

        "operation": "COMPARE_QUOTATIONS",

        "intent": "QUOTATION",

        "rfq_number": "RFQ-000013",

        "vendor_id": "VENDOR-004",

        "quotation_id": "QUO-019",
    }

    result = memory_update_node(state)

    assert result["last_operation"] == "COMPARE_QUOTATIONS"

    assert result["last_intent"] == "QUOTATION"

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000013"

    assert context["active_vendor"] == "VENDOR-004"

    assert context["active_quotation"] == "QUO-019"


# ============================================================
# TEST 8
# Empty state should not create unnecessary memory
# ============================================================

def test_memory_update_empty_state():

    state = {
        "user_query": "Hello"
    }

    result = memory_update_node(state)

    assert result == {}





# ============================================================
# TEST 9
# Memory update extracts live quotation result
# ============================================================

def test_memory_update_extracts_live_data():

    state = {
        "user_query": "Get quotations for RFQ-000013",

        "operation": "GET_QUOTATIONS",

        "intent": "QUOTATION",

        "rfq_number": "RFQ-000013",

        "live_data": {
            "found": True,

            "rfq_number": "RFQ-000013",

            "quotation_count": 2,

            "quotations": [
                {
                    "quotation_number": "QUO-001",
                    "vendor_id": 4,
                    "total_amount": 47200,
                    "currency": "INR",
                },
                {
                    "quotation_number": "QUO-002",
                    "vendor_id": 5,
                    "total_amount": 51000,
                    "currency": "INR",
                },
            ],
        },

        "conversation_context": {},
    }

    result = memory_update_node(state)

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000013"

    assert len(
        context["referenced_entities"]
    ) == 2

    assert (
        context["referenced_entities"][0]["entity_id"]
        == 4
    )

    assert (
        context["referenced_entities"][0]["quotation_number"]
        == "QUO-001"
    )


# ============================================================
# TEST 10
# Comparison result creates cheapest vendor memory
# ============================================================

def test_memory_update_extracts_cheapest_vendor():

    state = {
        "user_query": "Compare quotations for RFQ-000013",

        "operation": "COMPARE_QUOTATIONS",

        "intent": "QUOTATION",

        "rfq_number": "RFQ-000013",

        "live_data": {
            "found": True,

            "rfq_number": "RFQ-000013",

            "comparison": {
                "rfq_id": 13,

                "rfq_number": "RFQ-000013",

                "title": "Laptop Procurement",

                "quotation_count": 2,

                "quotations": [
                    {
                        "rank": 1,
                        "quotation_id": 101,
                        "vendor_id": 4,
                        "vendor_name": "ABC Supplies",
                        "vendor_code": "ABC-001",
                        "total_amount": 42500,
                        "currency": "INR",
                        "delivery_days": None,
                        "payment_terms": None,
                        "validity_date": None,
                    },
                    {
                        "rank": 2,
                        "quotation_id": 102,
                        "vendor_id": 5,
                        "vendor_name": "XYZ Traders",
                        "vendor_code": "XYZ-001",
                        "total_amount": 47000,
                        "currency": "INR",
                        "delivery_days": None,
                        "payment_terms": None,
                        "validity_date": None,
                    },
                ],

                "item_comparison": [],
            },
        },

        "conversation_context": {},
    }

    result = memory_update_node(state)

    context = result["conversation_context"]

    assert context["active_rfq"] == "RFQ-000013"

    cheapest = context["cheapest_vendor"]

    assert cheapest["vendor_id"] == 4

    assert cheapest["quotation_id"] == 101

    assert cheapest["vendor_name"] == "ABC Supplies"

    assert cheapest["total_amount"] == 42500


# ============================================================
# TEST 11
# Existing context is preserved
# ============================================================

def test_memory_update_preserves_context_with_live_data():

    state = {
        "user_query": "Compare quotations",

        "operation": "COMPARE_QUOTATIONS",

        "intent": "QUOTATION",

        "rfq_number": "RFQ-000013",

        "conversation_context": {
            "active_vendor": 99,
            "active_quotation": 500,
        },

        "live_data": {
            "found": True,

            "rfq_number": "RFQ-000013",

            "comparison": {
                "quotations": [
                    {
                        "rank": 1,
                        "quotation_id": 101,
                        "vendor_id": 4,
                        "vendor_name": "ABC Supplies",
                        "vendor_code": "ABC-001",
                        "total_amount": 42500,
                        "currency": "INR",
                    },
                ],
            },
        },
    }

    result = memory_update_node(state)

    context = result["conversation_context"]

    # Existing context must survive.

    assert context["active_vendor"] == 99

    assert context["active_quotation"] == 500

    # New context must also be added.

    assert context["active_rfq"] == "RFQ-000013"

    assert context["cheapest_vendor"]["vendor_id"] == 4


# ============================================================
# TEST 12
# No live data should still update routing memory
# ============================================================

def test_memory_update_without_live_data():

    state = {
        "user_query": "Compare quotations",

        "operation": "COMPARE_QUOTATIONS",

        "intent": "QUOTATION",

    }

    result = memory_update_node(state)

    assert (
        result["last_operation"]
        == "COMPARE_QUOTATIONS"
    )

    assert (
        result["last_intent"]
        == "QUOTATION"
    )

    assert (
        "conversation_context"
        not in result
    )