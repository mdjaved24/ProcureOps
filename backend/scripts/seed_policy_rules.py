import json

from sqlalchemy import text

from app.core.database import SessionLocal




POLICY_CODE = "PROCUREMENT-001"


POLICY_RULES = [
    {
        "rule_code": "PROCUREMENT-VALUE-001",
        "name": "High Value Procurement",
        "description": (
            "Procurement requests above INR 25 lakh "
            "require Procurement Head approval."
        ),
        "priority": 100,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN",
            "value": 2500000,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_HEAD",
        },
    },
    {
        "rule_code": "PROCUREMENT-VALUE-002",
        "name": "Executive Financial Approval",
        "description": (
            "Procurement requests above INR 50 lakh "
            "require CFO approval."
        ),
        "priority": 90,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN",
            "value": 5000000,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "CFO",
        },
    },
    {
        "rule_code": "PROCUREMENT-SECURITY-001",
        "name": "Restricted Data Processing",
        "description": (
            "Procurement involving restricted data "
            "requires Security Officer approval."
        ),
        "priority": 80,
        "condition": {
            "field": "data_classification",
            "operator": "EQUALS",
            "value": "RESTRICTED",
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "SECURITY_OFFICER",
        },
    },
]


def seed_policy_rules():
    db = SessionLocal()

    try:
        policy_id = db.execute(
            text(
                """
                SELECT id
                FROM policies
                WHERE policy_code = :policy_code
                """
            ),
            {
                "policy_code": POLICY_CODE,
            },
        ).scalar_one_or_none()

        if policy_id is None:
            raise RuntimeError(
                f"Policy '{POLICY_CODE}' was not found."
            )

        for rule in POLICY_RULES:
            db.execute(
                text(
                    """
                    INSERT INTO policy_rules (
                        policy_id,
                        rule_code,
                        name,
                        description,
                        priority,
                        condition,
                        action,
                        is_active
                    )
                    VALUES (
                        :policy_id,
                        :rule_code,
                        :name,
                        :description,
                        :priority,
                        CAST(:condition AS jsonb),
                        CAST(:action AS jsonb),
                        TRUE
                    )
                    ON CONFLICT (rule_code)
                    DO NOTHING
                    """
                ),
                {
                    "policy_id": policy_id,
                    "rule_code": rule["rule_code"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "priority": rule["priority"],
                    "condition": json.dumps(rule["condition"]),
                    "action": json.dumps(rule["action"]),
                },
            )

        db.commit()

        print("Policy rules seeded successfully.")

    except Exception as exc:
        db.rollback()
        print(f"Failed to seed policy rules: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_policy_rules()