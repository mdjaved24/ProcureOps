from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy.policy import Policy
from app.models.policy.policy_rule import PolicyRule


SUPPORTED_OPERATORS = {
    "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL",
    "LESS_THAN",
    "LESS_THAN_OR_EQUAL",
    "EQUALS",
    "NOT_EQUALS",
}


class PolicyEngine:

    @staticmethod
    def evaluate_condition(
        condition: dict[str, Any],
        context: dict[str, Any]
    ) -> bool:
        field = condition.get('field')
        operator = condition.get("operator")
        expected_value = condition.get("value")

        if not field or not operator:
            return False

        if operator not in SUPPORTED_OPERATORS:
            return False

        actual_value = context.get(field)

        if not actual_value:
            return False

        # Normalize numeric values.
        if isinstance(actual_value, Decimal):
            if isinstance(expected_value, (int, float)):
                expected_value = Decimal(
                    str(expected_value)
                )


        if operator == "GREATER_THAN":
            return actual_value > expected_value

        if operator == "GREATER_THAN_OR_EQUAL":
            return actual_value >= expected_value

        if operator == "LESS_THAN":
            return actual_value < expected_value

        if operator == "LESS_THAN_OR_EQUAL":
            return actual_value <= expected_value

        if operator == "EQUALS":
            return actual_value == expected_value

        if operator == "NOT_EQUALS":
            return actual_value != expected_value

        return False


    @staticmethod
    def evaluate(
        db: Session,
        policy_code: str,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        policy = db.query(Policy).filter(
            Policy.policy_code==policy_code, 
            Policy.is_active.is_(True)
            ).first()

        if policy is None:
            return []

        rules = db.query(PolicyRule).filter(
            PolicyRule.policy_id==policy.id,
            PolicyRule.is_active.is_(True)
        ).order_by(PolicyRule.priority.desc()).all()

        decisions = []

        for rule in rules:
            matched = PolicyEngine.evaluate_condition(
                condition=rule.condition,
                context=context
            )

            if matched:
                decisions.append(
                    {
                        "rule_code": rule.rule_code,
                        "rule_name": rule.name,
                        "action": rule.action,
                    }
                )

        return decisions
    
