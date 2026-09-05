from sqlalchemy.orm import Session
import logging

from app.cache.cache_service import CacheService
from app.models.policy.policy import Policy
from app.services.policy.policy_resolver import PolicyResolver

logger = logging.getLogger(__name__)


class PolicyService:

    @staticmethod
    def update_policy_version(
        db: Session,
        policy_id: int,
        new_version: str,
    ) -> Policy:
        """
        Update policy version and invalidate cache.
        """
        policy = db.get(Policy, policy_id)

        if policy is None:
            raise ValueError("Policy not found")

        old_version = policy.version
        policy.version = new_version

        try:
            db.commit()
            db.refresh(policy)
            logger.info(f"Policy version updated: {policy.policy_code} {old_version} -> {new_version}")
        except Exception:
            db.rollback()
            logger.error(f"Failed to update policy version: {policy.policy_code}")
            raise

        # Invalidate cache for both old and new versions
        try:
            # Invalidate old version cache
            CacheService.invalidate_policy(
                policy_code=policy.policy_code,
                version=old_version,
            )
            logger.info(f"Cache invalidated for policy: {policy.policy_code}:v{old_version}")
            
            # Also invalidate new version cache (if it exists)
            CacheService.invalidate_policy(
                policy_code=policy.policy_code,
                version=new_version,
            )
            logger.info(f"Cache invalidated for policy: {policy.policy_code}:v{new_version}")
            
        except Exception as exc:
            logger.warning(f"Failed to invalidate policy cache: {exc}")

        return policy

    @staticmethod
    def refresh_policy_cache(
        db: Session,
        policy_code: str,
    ) -> dict:
        """
        Force refresh of policy cache.
        """
        
        
        # Get policy from database
        policy = db.query(Policy).filter(
            Policy.policy_code == policy_code,
            Policy.is_active.is_(True)
        ).first()
        
        if policy is None:
            raise ValueError(f"Policy not found: {policy_code}")
        
        # Invalidate existing cache
        cache_key = f"policy:{policy.policy_code}:v{policy.version}"
        CacheService.delete(cache_key)
        
        # Force reload by resolving
        context = {}  # Empty context for cache refresh
        policy_snapshot = PolicyResolver.resolve(db, context)
        
        return {
            "message": "Policy cache refreshed",
            "policy_code": policy_code,
            "version": policy.version,
            "cache_key": cache_key
        }