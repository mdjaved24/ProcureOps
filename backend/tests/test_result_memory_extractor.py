from app.ai.services.result_memory_extractor import (
    ResultMemoryExtractor,
)


# ============================================================
# TEST 1
# Basic RFQ extraction
# ============================================================

def test_extract_active_rfq():

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",
        "quotation_count": 0,
        "quotations": [],
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    assert (
        result["active_rfq"]
        == "RFQ-000013"
    )


# ============================================================
# TEST 2
# Extract quotations from get_rfq_quotations
# ============================================================

def test_extract_direct_quotations():

    live_data = {
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
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    entities = result[
        "referenced_entities"
    ]

    assert len(entities) == 2

    assert (
        entities[0]["entity_id"]
        == 4
    )

    assert (
    entities[0]["quotation_number"]
    == "QUO-001"
    )

    assert (
        entities[1]["entity_id"]
        == 5
    )


# ============================================================
# TEST 3
# Extract comparison quotations
# ============================================================

def test_extract_comparison_quotations():

    live_data = {
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
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    entities = result[
        "referenced_entities"
    ]

    assert len(entities) == 2

    assert (
        entities[0]["entity_id"]
        == 4
    )

    assert (
        entities[0]["entity_name"]
        == "ABC Supplies"
    )

    assert (
        entities[0]["quotation_id"]
        == 101
    )


# ============================================================
# TEST 4
# Identify cheapest vendor
# ============================================================

def test_extract_cheapest_vendor():

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",

        "comparison": {

            "quotation_count": 3,

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

                {
                    "rank": 2,
                    "quotation_id": 102,
                    "vendor_id": 5,
                    "vendor_name": "XYZ Traders",
                    "vendor_code": "XYZ-001",
                    "total_amount": 47000,
                    "currency": "INR",
                },

                {
                    "rank": 3,
                    "quotation_id": 103,
                    "vendor_id": 6,
                    "vendor_name": "PQR Ltd",
                    "vendor_code": "PQR-001",
                    "total_amount": 51000,
                    "currency": "INR",
                },
            ],

            "item_comparison": [],
        },
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    cheapest = result[
        "cheapest_vendor"
    ]

    assert (
        cheapest["vendor_id"]
        == 4
    )

    assert (
        cheapest["quotation_id"]
        == 101
    )

    assert (
        cheapest["vendor_name"]
        == "ABC Supplies"
    )

    assert (
        cheapest["total_amount"]
        == 42500
    )

    assert (
        cheapest["currency"]
        == "INR"
    )


# ============================================================
# TEST 5
# Cheapest vendor should NOT depend on rank
# ============================================================

def test_cheapest_vendor_calculated_from_amount():

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",

        "comparison": {

            "quotations": [

                {
                    "rank": 1,
                    "quotation_id": 101,
                    "vendor_id": 4,
                    "vendor_name": "ABC Supplies",
                    "total_amount": 50000,
                    "currency": "INR",
                },

                {
                    "rank": 2,
                    "quotation_id": 102,
                    "vendor_id": 5,
                    "vendor_name": "XYZ Traders",
                    "total_amount": 42000,
                    "currency": "INR",
                },
            ],

            "item_comparison": [],
        },
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    cheapest = result[
        "cheapest_vendor"
    ]

    assert (
        cheapest["vendor_id"]
        == 5
    )

    assert (
        cheapest["vendor_name"]
        == "XYZ Traders"
    )

    assert (
        cheapest["total_amount"]
        == 42000
    )


# ============================================================
# TEST 6
# No quotations
# ============================================================

def test_no_quotations():

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",

        "comparison": {
            "quotation_count": 0,
            "quotations": [],
            "item_comparison": [],
        },
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    assert (
        result["active_rfq"]
        == "RFQ-000013"
    )

    assert (
        "cheapest_vendor"
        not in result
    )


# ============================================================
# TEST 7
# RFQ not found
# ============================================================

def test_rfq_not_found():

    live_data = {
        "found": False,
        "rfq_number": "RFQ-999999",
        "message": "RFQ not found.",
        "comparison": None,
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    assert (
        result["active_rfq"]
        == "RFQ-999999"
    )

    assert (
        "cheapest_vendor"
        not in result
    )


# ============================================================
# TEST 8
# Empty data
# ============================================================

def test_empty_result():

    result = ResultMemoryExtractor.extract({})

    assert result == {}


# ============================================================
# TEST 9
# Malformed quotations are ignored
# ============================================================

def test_malformed_quotations_are_ignored():

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",

        "comparison": {

            "quotations": [

                None,

                "invalid",

                {},

                {
                    "quotation_id": 101,
                    "vendor_id": 4,
                    "vendor_name": "ABC Supplies",
                    "total_amount": 42500,
                    "currency": "INR",
                },
            ],

            "item_comparison": [],
        },
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    entities = result[
        "referenced_entities"
    ]

    assert len(entities) == 1

    assert (
    entities[0]["entity_name"]
    == "ABC Supplies"
    )


# ============================================================
# TEST 10
# JSON serializable
# ============================================================

def test_result_is_json_serializable():

    import json

    live_data = {
        "found": True,
        "rfq_number": "RFQ-000013",

        "comparison": {

            "quotations": [

                {
                    "quotation_id": 101,
                    "vendor_id": 4,
                    "vendor_name": "ABC Supplies",
                    "total_amount": 42500,
                    "currency": "INR",
                }
            ],

            "item_comparison": [],
        },
    }

    result = ResultMemoryExtractor.extract(
        live_data
    )

    json.dumps(result)