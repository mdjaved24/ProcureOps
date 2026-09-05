from unittest.mock import MagicMock

from app.ai.mcp.tools.vendor_tools import (
    VendorToolService,
)


def test_get_vendor_requires_identifier():

    db = MagicMock()

    result = VendorToolService.get_vendor(db=db)

    assert result["found"] is False
    assert "required" in result["message"]


def test_get_vendor_not_found():

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    result = VendorToolService.get_vendor(
        db=db,
        vendor_id=999999,
    )

    assert result["found"] is False
    assert result["message"] == "Vendor not found."


def test_search_vendors_returns_empty_result():

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .limit.return_value
        .all.return_value
    ) = []

    result = VendorToolService.search_vendors(
        db=db,
        search="nonexistent-vendor",
    )

    assert result["found"] is True
    assert result["count"] == 0
    assert result["vendors"] == []