from app.core.database import SessionLocal
from app.services.policy.policy_resolver import PolicyResolver


def main():
    db = SessionLocal()

    try:
        context = {
            "estimated_amount": 3500000,
        }

        print("Resolving policy...")

        policy = PolicyResolver.resolve(
            db=db,
            context=context,
        )

        print("\nPolicy:")
        print(policy)

    finally:
        db.close()


if __name__ == "__main__":
    main()