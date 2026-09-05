import pytest

from app.ai.mcp.tools.quotation_action_service import (
    QuotationActionService,
)
from app.core.database import SessionLocal
from app.models.quotation.quotation import (
    Quotation,
    QuotationStatus,
)


def create_test_quotation(db, status: str) -> Quotation:
    """
    Create a minimal quotation for action-service testing.

    The quotation requires a valid rfq_vendor_id.
    Use an existing RFQVendor from the database.
    """

    from app.models.quotation_requests.rfq_vendor import RFQVendor

    rfq_vendor = (
        db.query(RFQVendor)
        .first()
    )

    if rfq_vendor is None:
        pytest.skip(
            "No RFQVendor exists in the database."
        )

    quotation = Quotation(
        rfq_vendor_id=rfq_vendor.id,
        quotation_number="QT-HITL-TEST",
        status=status,
        currency="INR",
        subtotal=100000,
        tax_amount=18000,
        total_amount=118000,
    )

    db.add(quotation)
    db.commit()
    db.refresh(quotation)

    return quotation


def delete_test_quotation(db, quotation_id: int):
    """
    Remove test quotation from the database.
    """

    quotation = (
        db.query(Quotation)
        .filter(Quotation.id == quotation_id)
        .first()
    )

    if quotation is not None:
        db.delete(quotation)
        db.commit()


# ==========================================================
# APPROVE
# ==========================================================


def test_approve_submitted_quotation():
    db = SessionLocal()
    quotation = None

    try:
        quotation = create_test_quotation(
            db=db,
            status=QuotationStatus.SUBMITTED.value,
        )

        result = QuotationActionService.approve_quotation(
            db=db,
            quotation_id=quotation.id,
        )

        assert result["success"] is True

        assert (
            result["message"]
            == "Quotation approved successfully."
        )

        assert (
            result["quotation"]["previous_status"]
            == QuotationStatus.SUBMITTED.value
        )

        assert (
            result["quotation"]["status"]
            == QuotationStatus.ACCEPTED.value
        )

        # Verify actual database state
        db.expire_all()

        updated_quotation = (
            db.query(Quotation)
            .filter(
                Quotation.id == quotation.id
            )
            .first()
        )

        assert updated_quotation.status == (
            QuotationStatus.ACCEPTED.value
        )

    finally:
        if quotation is not None:
            delete_test_quotation(
                db,
                quotation.id,
            )

        db.close()


# ==========================================================
# REJECT
# ==========================================================


def test_reject_submitted_quotation():
    db = SessionLocal()
    quotation = None

    try:
        quotation = create_test_quotation(
            db=db,
            status=QuotationStatus.SUBMITTED.value,
        )

        result = QuotationActionService.reject_quotation(
            db=db,
            quotation_id=quotation.id,
        )

        assert result["success"] is True

        assert (
            result["message"]
            == "Quotation rejected successfully."
        )

        assert (
            result["quotation"]["previous_status"]
            == QuotationStatus.SUBMITTED.value
        )

        assert (
            result["quotation"]["status"]
            == QuotationStatus.REJECTED.value
        )

        # Verify actual database state
        db.expire_all()

        updated_quotation = (
            db.query(Quotation)
            .filter(
                Quotation.id == quotation.id
            )
            .first()
        )

        assert updated_quotation.status == (
            QuotationStatus.REJECTED.value
        )

    finally:
        if quotation is not None:
            delete_test_quotation(
                db,
                quotation.id,
            )

        db.close()


# ==========================================================
# INVALID APPROVAL
# ==========================================================


@pytest.mark.parametrize(
    "initial_status",
    [
        QuotationStatus.DRAFT.value,
        QuotationStatus.ACCEPTED.value,
        QuotationStatus.REJECTED.value,
        QuotationStatus.WITHDRAWN.value,
    ],
)
def test_cannot_approve_non_submitted_quotation(
    initial_status,
):
    db = SessionLocal()
    quotation = None

    try:
        quotation = create_test_quotation(
            db=db,
            status=initial_status,
        )

        result = QuotationActionService.approve_quotation(
            db=db,
            quotation_id=quotation.id,
        )

        assert result["success"] is False

        assert (
            result["message"]
            == "Only submitted quotations can be approved."
        )

        # Verify status did not change
        db.expire_all()

        unchanged_quotation = (
            db.query(Quotation)
            .filter(
                Quotation.id == quotation.id
            )
            .first()
        )

        assert unchanged_quotation.status == (
            initial_status
        )

    finally:
        if quotation is not None:
            delete_test_quotation(
                db,
                quotation.id,
            )

        db.close()


# ==========================================================
# INVALID REJECTION
# ==========================================================


@pytest.mark.parametrize(
    "initial_status",
    [
        QuotationStatus.DRAFT.value,
        QuotationStatus.ACCEPTED.value,
        QuotationStatus.REJECTED.value,
        QuotationStatus.WITHDRAWN.value,
    ],
)
def test_cannot_reject_non_submitted_quotation(
    initial_status,
):
    db = SessionLocal()
    quotation = None

    try:
        quotation = create_test_quotation(
            db=db,
            status=initial_status,
        )

        result = QuotationActionService.reject_quotation(
            db=db,
            quotation_id=quotation.id,
        )

        assert result["success"] is False

        assert (
            result["message"]
            == "Only submitted quotations can be rejected."
        )

        # Verify status did not change
        db.expire_all()

        unchanged_quotation = (
            db.query(Quotation)
            .filter(
                Quotation.id == quotation.id
            )
            .first()
        )

        assert unchanged_quotation.status == (
            initial_status
        )

    finally:
        if quotation is not None:
            delete_test_quotation(
                db,
                quotation.id,
            )

        db.close()


# ==========================================================
# QUOTATION NOT FOUND
# ==========================================================


def test_approve_nonexistent_quotation():
    db = SessionLocal()

    try:
        result = QuotationActionService.approve_quotation(
            db=db,
            quotation_id=999999999,
        )

        assert result["success"] is False

        assert (
            result["message"]
            == "Quotation not found."
        )

    finally:
        db.close()


def test_reject_nonexistent_quotation():
    db = SessionLocal()

    try:
        result = QuotationActionService.reject_quotation(
            db=db,
            quotation_id=999999999,
        )

        assert result["success"] is False

        assert (
            result["message"]
            == "Quotation not found."
        )

    finally:
        db.close()