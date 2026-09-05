import pytest

from app.ai.services.operation_resolver import OperationResolver
    

# ==========================================================
# APPROVE QUOTATION
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Approve quotation 123",
        "Approve quotation QT-123",
        "approve quote 123",
        "Please approve quotation 123",
        "Please approve quote QT-123",
        "Accept quotation 123",
        "accept quote QT-123",
    ],
)
def test_resolve_approve_quotation(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "APPROVE_QUOTATION"


# ==========================================================
# REJECT QUOTATION
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Reject quotation 123",
        "Reject quotation QT-123",
        "reject quote 123",
        "Please reject quotation 123",
        "Please reject quote QT-123",
        "Decline quotation 123",
        "decline quote QT-123",
    ],
)
def test_resolve_reject_quotation(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "REJECT_QUOTATION"


# ==========================================================
# COMPARE QUOTATIONS
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Compare quotation",
        "Compare quotations",
        "Compare quote",
        "Compare quotes",
        "Compare them",
        "Compare those",
        "Compare these",
        "Compare it",
        "Show comparison",
        "Show the comparison",
    ],
)
def test_resolve_compare_quotations(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "COMPARE_QUOTATIONS"


# ==========================================================
# GET QUOTATIONS
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Show quotation",
        "Show quotations",
        "Get quotation",
        "Get quotations",
        "List quotation",
        "List quotations",
        "Show them",
        "Show those",
        "Show these",
    ],
)
def test_resolve_get_quotations(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "GET_QUOTATIONS"


# ==========================================================
# RFQ STATUS
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "RFQ status",
        "Status of RFQ",
        "What is its status",
        "What's its status",
        "Show its status",
        "Show the status",
    ],
)
def test_resolve_rfq_status(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "GET_RFQ_STATUS"


# ==========================================================
# SEARCH VENDORS
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Search vendor",
        "Search vendors",
        "Find vendor",
        "Find vendors",
        "List vendor",
        "List vendors",
    ],
)
def test_resolve_search_vendors(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "SEARCH_VENDORS"


# ==========================================================
# GET VENDOR
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Get vendor",
        "Show vendor",
        "Vendor details",
        "Vendor detail",
    ],
)
def test_resolve_get_vendor(query):
    result = OperationResolver.resolve_operation(query)

    assert result == "GET_VENDOR"


# ==========================================================
# GENERIC FOLLOW-UP
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "show it",
        "show that",
        "show details",
        "tell me more",
        "what about it",
    ],
)
def test_resolve_generic_follow_up(query):
    result = OperationResolver.resolve_operation(
        query,
        previous_operation="GET_QUOTATIONS",
    )

    assert result == "GET_QUOTATIONS"


# ==========================================================
# GENERIC FOLLOW-UP WITH DIFFERENT PREVIOUS OPERATION
# ==========================================================

def test_generic_follow_up_returns_previous_operation():
    result = OperationResolver.resolve_operation(
        "show it",
        previous_operation="COMPARE_QUOTATIONS",
    )

    assert result == "COMPARE_QUOTATIONS"


# ==========================================================
# NO OPERATION
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "",
        "hello",
        "help me",
        "show procurement",
        "what can you do",
        "give me information",
    ],
)
def test_resolve_operation_returns_none(query):
    result = OperationResolver.resolve_operation(query)

    assert result is None


# ==========================================================
# SENSITIVE ACTIONS MUST NOT BE IMPLIED
# ==========================================================

@pytest.mark.parametrize(
    "query",
    [
        "Approve it",
        "Approve that",
        "Approve this",
        "Reject it",
        "Reject that",
        "Reject this",
    ],
)
def test_sensitive_action_requires_explicit_quotation_action(query):
    result = OperationResolver.resolve_operation(
        query,
        previous_operation="GET_QUOTATIONS",
    )

    assert result is None