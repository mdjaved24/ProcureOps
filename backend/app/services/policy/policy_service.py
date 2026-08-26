from sqlalchemy.orm import Session

from app.infrastructure.cache.cache_service import CacheService
from app.models.policy.policy import Policy


class PolicyService:

    @staticmethod
    def update_policy_version(
        db: Session,
        policy_id: int,
        new_version: str,
    ) -> Policy:

        policy = db.get(
            Policy,
            policy_id,
        )

        if policy is None:
            raise ValueError(
                "Policy not found"
            )

        old_version = policy.version

        policy.version = new_version

        try:
            db.commit()
            db.refresh(policy)

        except Exception:
            db.rollback()
            raise

        # Redis is an optimization layer.
        # Database commit must succeed independently.
        try:
            CacheService.invalidate_policy(
                policy_code=policy.policy_code,
                version=old_version,
            )
        except Exception as exc:
            print(
                f"WARNING: Failed to invalidate "
                f"policy cache: {exc}"
            )

        return policy