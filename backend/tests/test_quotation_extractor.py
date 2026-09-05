import pytest

from app.ai.mcp.tools.quotation_extractor import QuotationExtractor


@pytest.mark.parametrize(
    "query, expected",
    [
        ("Approve quotation 123", 123),
        ("Approve quotation id 123", 123),
        ("Approve quotation: 123", 123),
        ("Approve quote 123", 123),
        ("Reject quote #456", 456),
        ("Reject quotation-789", 789),
    ],
)
def test_extract_quotation_id(query, expected):
    assert (
        QuotationExtractor.extract_quotation_id(query)
        == expected
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        ("Approve QT-123", "QT-123"),
        ("Approve qt-123", "QT-123"),
        ("Reject QT_456", "QT-456"),
        ("Reject quotation QT-789", "QT-789"),
    ],
)
def test_extract_quotation_number(query, expected):
    assert (
        QuotationExtractor.extract_quotation_number(query)
        == expected
    )


@pytest.mark.parametrize(
    "query",
    [
        "Approve quotation",
        "Reject quote",
        "Show vendors",
        "Compare RFQ-123",
    ],
)
def test_extract_quotation_id_returns_none(query):
    assert (
        QuotationExtractor.extract_quotation_id(query)
        is None
    )


@pytest.mark.parametrize(
    "query",
    [
        "Approve quotation",
        "Reject quote",
        "Show vendors",
        "Compare RFQ-123",
    ],
)
def test_extract_quotation_number_returns_none(query):
    assert (
        QuotationExtractor.extract_quotation_number(query)
        is None
    )