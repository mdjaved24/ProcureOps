from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.cache.cache_service import CacheService
from app.models.policy.policy import Policy
from app.models.policy.policy_rule import PolicyRule


class PolicyResolver:

    DEFAULT_POLICY_CODE = "PROCUREMENT-001"
    CACHE_TTL_SECONDS = 3600

    @staticmethod
    def resolve(
        db: Session,
        context: dict[str, Any],
    ) -> dict[str, Any]:

        # Resolve the policy definition.
        policy = db.query(Policy).filter(
            Policy.policy_code==PolicyResolver.DEFAULT_POLICY_CODE,
            Policy.is_active.is_(True)
        ).first()


        if policy is None:
            raise ValueError(
                "No active procurement policy is available"
            )

        cache_key = (
            f"policy:{policy.policy_code}:"
            f"v{policy.version}"
        )

        cached_policy = CacheService.get(cache_key)

        if cached_policy is not None:
            print(
                f"[CACHE HIT] {cache_key}"
            )
            return cached_policy


        print(
            f"[CACHE MISS] {cache_key}"
        )


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

        CacheService.set(
            key=cache_key,
            value=policy_snapshot,
            ttl_seconds=PolicyResolver.CACHE_TTL_SECONDS,
        )

        return policy_snapshot