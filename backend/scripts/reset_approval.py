from app.core.database import SessionLocal
from app.models.approval.approval import Approval, ApprovalStatus
from app.models.approval.approval_step import (
    ApprovalStep,
    ApprovalStepStatus,
)


def main():
    db = SessionLocal()

    try:
        approval = db.get(Approval, 1)

        if approval is None:
            print("Approval not found")
            return

        approval.status = ApprovalStatus.PENDING.value

        for step in approval.steps:
            step.status = ApprovalStepStatus.PENDING.value
            step.decided_by = None
            step.decision_at = None
            step.decision_comments = None

        db.commit()

        print("Approval reset successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()