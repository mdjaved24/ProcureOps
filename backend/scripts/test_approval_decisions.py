from decimal import Decimal

from fastapi import HTTPException

from app.core.database import SessionLocal
from app.models.approval.approval import (
    Approval,
    ApprovalStatus,
)
from app.models.approval.approval_step import (
    ApprovalStep,
    ApprovalStepStatus,
)
from app.models.identity.user import User
from app.models.procurement.purchase_request import (
    PurchaseRequest,
    PurchaseRequestStatus,
)
from app.schemas.approval.approval_decision import (
    ApprovalDecision,
)
from app.services.approval.approval_decision_service import (
    ApprovalDecisionService,
)


def get_user_by_role(
    db,
    role_name: str,
):
    user = (
        db.query(User)
        .filter(
            User.is_active.is_(True),
        )
        .filter(
            User.role.has(name=role_name),
        )
        .first()
    )

    if user is None:
        raise RuntimeError(
            f"No active user found for role: {role_name}"
        )

    return user


def create_test_approval(db):
    """
    Create a minimal approval workflow directly
    for service-level testing.

    The caller controls the transaction, so the
    created records can be rolled back after testing.
    """

    requester = get_user_by_role(
        db,
        "EMPLOYEE",
    )

    purchase_request = PurchaseRequest(
        request_number=f"TEST-PR-{id(object())}",
        title="Automated Approval Test",
        description=(
            "Created by approval decision test"
        ),
        requester_id=requester.id,
        department_id=requester.department_id,
        estimated_amount=Decimal("3500000"),
        currency="INR",
        status=(
            PurchaseRequestStatus
            .APPROVAL_PENDING
            .value
        ),
    )

    db.add(purchase_request)
    db.flush()

    approval = Approval(
        purchase_request_id=purchase_request.id,
        status=ApprovalStatus.PENDING.value,
        approval_type="ALL_REQUIRED",
    )

    db.add(approval)
    db.flush()

    step = ApprovalStep(
        approval_id=approval.id,
        required_role="PROCUREMENT_HEAD",
        sequence=1,
        status=ApprovalStepStatus.PENDING.value,
    )

    db.add(step)
    db.flush()

    return (
        purchase_request,
        approval,
        step,
    )


def test_unauthorized(db):
    print("\n" + "=" * 60)
    print("TEST 1: Unauthorized approval")
    print("=" * 60)

    _, _, step = create_test_approval(db)

    employee = get_user_by_role(
        db,
        "EMPLOYEE",
    )

    try:
        ApprovalDecisionService.decide(
            db=db,
            approval_step_id=step.id,
            current_user=employee,
            decision=ApprovalDecision.APPROVE,
            comments="Unauthorized test",
        )

        print("❌ FAILED")
        print(
            "Employee was allowed to approve."
        )

    except HTTPException as exc:

        if exc.status_code == 403:
            print("✅ PASSED")
            print(
                "Employee correctly received 403."
            )
        else:
            print("❌ FAILED")
            print(
                f"Expected 403, got {exc.status_code}"
            )


def test_reject(db):
    print("\n" + "=" * 60)
    print("TEST 2: Reject approval")
    print("=" * 60)

    (
        purchase_request,
        approval,
        step,
    ) = create_test_approval(db)

    procurement_head = get_user_by_role(
        db,
        "PROCUREMENT_HEAD",
    )

    result = ApprovalDecisionService.decide(
        db=db,
        approval_step_id=step.id,
        current_user=procurement_head,
        decision=ApprovalDecision.REJECT,
        comments="Automated rejection test",
    )

    db.refresh(purchase_request)
    db.refresh(approval)
    db.refresh(step)

    passed = (
        result.status
        == ApprovalStatus.REJECTED.value
        and approval.status
        == ApprovalStatus.REJECTED.value
        and step.status
        == ApprovalStepStatus.REJECTED.value
        and purchase_request.status
        == PurchaseRequestStatus.REJECTED.value
    )

    if passed:
        print("✅ PASSED")
        print("Approval = REJECTED")
        print("Step = REJECTED")
        print(
            "Purchase Request = REJECTED"
        )
    else:
        print("❌ FAILED")
        print(
            f"Approval: {approval.status}"
        )
        print(
            f"Step: {step.status}"
        )
        print(
            f"PR: {purchase_request.status}"
        )


def test_request_changes(db):
    print("\n" + "=" * 60)
    print("TEST 3: Request changes")
    print("=" * 60)

    (
        purchase_request,
        approval,
        step,
    ) = create_test_approval(db)

    procurement_head = get_user_by_role(
        db,
        "PROCUREMENT_HEAD",
    )

    result = ApprovalDecisionService.decide(
        db=db,
        approval_step_id=step.id,
        current_user=procurement_head,
        decision=(
            ApprovalDecision.REQUEST_CHANGES
        ),
        comments=(
            "Please provide additional "
            "justification."
        ),
    )

    db.refresh(purchase_request)
    db.refresh(approval)
    db.refresh(step)

    passed = (
        result.status
        == ApprovalStatus.CHANGES_REQUESTED.value
        and approval.status
        == ApprovalStatus.CHANGES_REQUESTED.value
        and step.status
        == ApprovalStepStatus.REJECTED.value
        and purchase_request.status
        == PurchaseRequestStatus.CHANGES_REQUESTED.value
    )

    if passed:
        print("✅ PASSED")
        print(
            "Approval = CHANGES_REQUESTED"
        )
        print("Step = REJECTED")
        print(
            "Purchase Request = CHANGES_REQUESTED"
        )
    else:
        print("❌ FAILED")
        print(
            f"Approval: {approval.status}"
        )
        print(
            f"Step: {step.status}"
        )
        print(
            f"PR: {purchase_request.status}"
        )


def test_duplicate_decision(db):
    print("\n" + "=" * 60)
    print("TEST 4: Duplicate decision")
    print("=" * 60)

    _, _, step = create_test_approval(db)

    procurement_head = get_user_by_role(
        db,
        "PROCUREMENT_HEAD",
    )

    ApprovalDecisionService.decide(
        db=db,
        approval_step_id=step.id,
        current_user=procurement_head,
        decision=ApprovalDecision.APPROVE,
        comments="First approval",
    )

    try:
        ApprovalDecisionService.decide(
            db=db,
            approval_step_id=step.id,
            current_user=procurement_head,
            decision=ApprovalDecision.APPROVE,
            comments="Duplicate approval",
        )

        print("❌ FAILED")
        print(
            "Duplicate decision was accepted."
        )

    except HTTPException as exc:

        if exc.status_code == 409:
            print("✅ PASSED")
            print(
                "Duplicate decision correctly "
                "returned 409."
            )
        else:
            print("❌ FAILED")
            print(
                f"Expected 409, got {exc.status_code}"
            )


def run_test(test_function):
    """
    Run each scenario inside an isolated
    transaction and rollback afterwards.
    """

    db = SessionLocal()

    try:
        test_function(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.rollback()
        db.close()


def main():

    run_test(test_unauthorized)
    run_test(test_reject)
    run_test(test_request_changes)
    run_test(test_duplicate_decision)

    print("\n" + "=" * 60)
    print(
        "Approval decision tests completed"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()