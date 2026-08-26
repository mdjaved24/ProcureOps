from app.core.database import SessionLocal
from app.services.policy.policy_service import PolicyService


def main():
    db = SessionLocal()

    try:
        policy = PolicyService.update_policy_version(
            db=db,
            policy_id=1,
            new_version="2.0",
        )

        print("\nUpdated policy:")
        print(
            {
                "id": policy.id,
                "policy_code": policy.policy_code,
                "version": policy.version,
            }
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()