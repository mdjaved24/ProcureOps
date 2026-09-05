from decimal import Decimal
from typing import Any
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy.policy import Policy
from app.models.policy.policy_rule import PolicyRule

logger = logging.getLogger(__name__)

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
        """
        Evaluate a single condition against the context.
        """
        field = condition.get('field')
        operator = condition.get("operator")
        expected_value = condition.get("value")

        if not field or not operator:
            logger.debug(f"Invalid condition: missing field or operator")
            return False

        if operator not in SUPPORTED_OPERATORS:
            logger.warning(f"Unsupported operator: {operator}")
            return False

        actual_value = context.get(field)

        if actual_value is None:
            logger.debug(f"Field '{field}' not found in context")
            return False

        # Normalize numeric values for comparison
        if isinstance(actual_value, (int, float, Decimal)):
            if isinstance(expected_value, (int, float)):
                expected_value = Decimal(str(expected_value))
            elif isinstance(expected_value, Decimal):
                pass  # Already Decimal
            else:
                try:
                    expected_value = Decimal(str(expected_value))
                except:
                    logger.warning(f"Could not convert expected_value to Decimal: {expected_value}")
                    return False

            # Convert actual_value to Decimal for comparison
            if not isinstance(actual_value, Decimal):
                actual_value = Decimal(str(actual_value))

        # Perform comparison based on operator
        try:
            if operator == "GREATER_THAN":
                return actual_value > expected_value
            elif operator == "GREATER_THAN_OR_EQUAL":
                return actual_value >= expected_value
            elif operator == "LESS_THAN":
                return actual_value < expected_value
            elif operator == "LESS_THAN_OR_EQUAL":
                return actual_value <= expected_value
            elif operator == "EQUALS":
                return actual_value == expected_value
            elif operator == "NOT_EQUALS":
                return actual_value != expected_value
            else:
                logger.warning(f"Unhandled operator: {operator}")
                return False
        except TypeError as e:
            logger.error(f"Type error in condition evaluation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in condition evaluation: {e}")
            return False

    @staticmethod
    def evaluate_policy(
        policy: dict[str, Any],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Evaluate all rules in a policy against the context.
        Returns a list of decisions.
        """
        decisions = []
        rules = policy.get("rules", [])
        
        logger.info(f"Evaluating {len(rules)} rules against context")
        logger.debug(f"Context: {context}")

        for rule in rules:
            condition = rule.get("condition", {})
            
            # Skip rules without conditions
            if not condition:
                logger.debug(f"Rule {rule.get('rule_code')} has no condition, skipping")
                continue

            matched = PolicyEngine.evaluate_condition(
                condition=condition,
                context=context,
            )

            if matched:
                logger.info(f"Rule triggered: {rule.get('rule_code')} - {rule.get('name')}")
                decisions.append({
                    "rule_code": rule["rule_code"],
                    "rule_name": rule["name"],
                    "action": rule.get("action", {}),
                    "priority": rule.get("priority", 0),
                })

        # If no decisions were triggered, add a default approval rule
        if not decisions:
            logger.warning("No policy rules triggered - adding default approval rule")
            
            # Determine the appropriate default approver based on amount
            estimated_amount = context.get("estimated_amount", 0)
            
            if estimated_amount < 50000:
                default_role = "PROCUREMENT_MANAGER"
                rule_name = "Low Value Default Approval"
            elif estimated_amount < 500000:
                default_role = "PROCUREMENT_HEAD"
                rule_name = "Medium Value Default Approval"
            else:
                default_role = "CFO"
                rule_name = "High Value Default Approval"
            
            decisions.append({
                "rule_code": "DEFAULT-APPROVAL",
                "rule_name": rule_name,
                "action": {
                    "type": "REQUIRE_APPROVAL",
                    "role": default_role
                },
                "priority": 0,
                "is_default": True
            })
            logger.info(f"Added default approval rule: {rule_name} with role: {default_role}")

        # Sort decisions by priority (higher priority first)
        decisions.sort(key=lambda x: x.get("priority", 0), reverse=True)

        logger.info(f"Generated {len(decisions)} decision(s)")
        return decisions