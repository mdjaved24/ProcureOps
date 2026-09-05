from app.ai.mcp.tools.vendor_extractor import VendorExtractor


def test_extract_vendor_id():
    assert (
        VendorExtractor.extract_vendor_id(
            "Show vendor 12"
        )
        == 12
    )


def test_extract_vendor_code():
    assert (
        VendorExtractor.extract_vendor_code(
            "Show vendor VND-001"
        )
        == "VND-001"
    )


def test_extract_vendor_status_active():
    assert (
        VendorExtractor.extract_vendor_status(
            "Find active vendors"
        )
        == "ACTIVE"
    )


def test_extract_vendor_status_inactive():
    assert (
        VendorExtractor.extract_vendor_status(
            "Find inactive vendors"
        )
        == "INACTIVE"
    )


def test_extract_vendor_search():
    assert (
        VendorExtractor.extract_vendor_search(
            "Search for Acme"
        )
        == "Acme"
    )


def test_extract_vendor_search_find():
    assert (
        VendorExtractor.extract_vendor_search(
            "Find Acme vendors"
        )
        == "Acme"
    )