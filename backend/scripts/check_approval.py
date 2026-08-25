from sqlalchemy import text

from app.core.database import SessionLocal


PURCHASE_REQUEST_ID = 1


def main():
    db = SessionLocal()

    try:
        approval = db.execute(
            text(
                """
                SELECT
                    id,
                    purchase_request_id,
                    status,
                    approval_type
                FROM approvals
                WHERE purchase_request_id = :request_id
                ORDER BY id DESC
                LIMIT 1
                """
            ),
            {
                "request_id": PURCHASE_REQUEST_ID,
            },
        ).mappings().first()

        print("\nApproval:")
        print(approval)

        if approval:
            steps = db.execute(
                text(
                    """
                    SELECT
                        id,
                        required_role,
                        sequence,
                        status,
                        approved_by,
                        decision_at
                    FROM approval_steps
                    WHERE approval_id = :approval_id
                    ORDER BY sequence
                    """
                ),
                {
                    "approval_id": approval["id"],
                },
            ).mappings().all()

            print("\nApproval Steps:")

            for step in steps:
                print(dict(step))

    finally:
        db.close()


if __name__ == "__main__":
    main()