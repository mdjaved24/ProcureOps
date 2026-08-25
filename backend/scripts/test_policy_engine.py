from decimal import Decimal


from app.core.database import SessionLocal
from app.services.policy.policy_engine import PolicyEngine


def main():
    db = SessionLocal()

    try:
        test_cases = [
            (
                "35 lakh procurement",
                {
                    "estimated_amount": Decimal("3500000")
                },
            ),
            (
                "60 lakh procurement",
                {
                    "estimated_amount": Decimal("6000000")
                },
            ),
            (
                "Restricted data procurement",
                {
                    "estimated_amount": Decimal("1000000"),
                    "data_classification": "RESTRICTED",
                },
            ),
        ]

        for name, context in test_cases:
            print("\n" + "=" * 60)
            print(name)
            print("Context:", context)

            decisions = PolicyEngine.evaluate(
                db=db,
                policy_code="PROCUREMENT-001",
                context=context,
            )

            print("Decisions:")

            for decision in decisions:
                print(
                    f"  - {decision['rule_code']}"
                )
                print(
                    f"    {decision['action']}"
                )

            if not decisions:
                print("  No policy rules matched.")

    finally:
        db.close()


if __name__ == "__main__":
    main()