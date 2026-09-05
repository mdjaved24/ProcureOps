from typing import Any, Optional
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cache.cache_service import CacheService
from app.models.policy.policy import Policy
from app.models.policy.policy_rule import PolicyRule

logger = logging.getLogger(__name__)


class PolicyResolver:

    DEFAULT_POLICY_CODE = "PROCUREMENT-001"
    CACHE_TTL_SECONDS = 3600

    @staticmethod
    def resolve(
        db: Session,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve the policy definition with cache fallback.
        """
        # Try to get policy from database first
        policy = db.query(Policy).filter(
            Policy.policy_code == PolicyResolver.DEFAULT_POLICY_CODE,
            Policy.is_active.is_(True)
        ).first()

        if policy is None:
            logger.warning(f"No active policy found with code: {PolicyResolver.DEFAULT_POLICY_CODE}")
            # Return a default policy if none exists in database
            return PolicyResolver._get_default_policy()

        cache_key = f"policy:{policy.policy_code}:v{policy.version}"

        # Try to get from cache
        try:
            cached_policy = CacheService.get(cache_key)
            if cached_policy is not None:
                logger.info(f"[CACHE HIT] {cache_key}")
                return cached_policy
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")

        logger.info(f"[CACHE MISS] {cache_key} - Loading from database")

        # Load from database
        try:
            rules = db.query(PolicyRule).filter(
                PolicyRule.policy_id == policy.id,
                PolicyRule.is_active.is_(True),
            ).order_by(
                PolicyRule.priority.desc()
            ).all()

            policy_snapshot = {
                "id": policy.id,
                "policy_code": policy.policy_code,
                "version": policy.version,
                "rules": [
                    {
                        "id": rule.id,
                        "rule_code": rule.rule_code,
                        "name": rule.name,
                        "priority": rule.priority,
                        "condition": rule.condition,
                        "action": rule.action,
                    }
                    for rule in rules
                ],
            }

            # Store in cache
            try:
                CacheService.set(
                    key=cache_key,
                    value=policy_snapshot,
                    ttl_seconds=PolicyResolver.CACHE_TTL_SECONDS,
                )
                logger.info(f"Policy cached successfully: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

            return policy_snapshot

        except Exception as e:
            logger.error(f"Error loading policy from database: {e}")
            # Return a default policy as fallback
            return PolicyResolver._get_default_policy()

    @staticmethod
    def _get_default_policy() -> dict[str, Any]:
        """
        Return a default policy with sensible rules.
        """
        logger.info("Using default policy configuration")
        
        return {
            "id": 0,
            "policy_code": "DEFAULT-POLICY",
            "version": "1.0",
            "rules": [
                {
                    "id": 1,
                    "rule_code": "LOW-VALUE-APPROVAL",
                    "name": "Low Value Procurement Approval",
                    "priority": 100,
                    "condition": {
                        "field": "estimated_amount",
                        "operator": "LESS_THAN",
                        "value": 50000
                    },
                    "action": {
                        "type": "REQUIRE_APPROVAL",
                        "role": "PROCUREMENT_MANAGER"
                    }
                },
                {
                    "id": 2,
                    "rule_code": "MEDIUM-VALUE-APPROVAL",
                    "name": "Medium Value Procurement Approval",
                    "priority": 90,
                    "condition": {
                        "field": "estimated_amount",
                        "operator": "LESS_THAN",
                        "value": 500000
                    },
                    "action": {
                        "type": "REQUIRE_APPROVAL",
                        "role": "PROCUREMENT_HEAD"
                    }
                },
                {
                    "id": 3,
                    "rule_code": "HIGH-VALUE-APPROVAL",
                    "name": "High Value Procurement Approval",
                    "priority": 80,
                    "condition": {
                        "field": "estimated_amount",
                        "operator": "GREATER_THAN_OR_EQUAL",
                        "value": 500000
                    },
                    "action": {
                        "type": "REQUIRE_APPROVAL",
                        "role": "CFO"
                    }
                },
                {
                    "id": 4,
                    "rule_code": "DEFAULT-APPROVAL",
                    "name": "Default Manager Approval (Fallback)",
                    "priority": 50,
                    "condition": {
                        "field": "estimated_amount",
                        "operator": "GREATER_THAN_OR_EQUAL",
                        "value": 0
                    },
                    "action": {
                        "type": "REQUIRE_APPROVAL",
                        "role": "PROCUREMENT_MANAGER"
                    }
                }
            ]
        }