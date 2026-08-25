from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy.policy import Policy


class PolicyResolver:

    DEFAULT_POLICY_CODE = "PROCUREMENT-001"

    @staticmethod
    def resolve(
        db: Session,
        context: dict[str, Any],
    ) -> Policy:
        """
        Resolve the procurement policy applicable
        to the given procurement context.

        Currently the platform has one active enterprise
        procurement policy. The resolver is intentionally
        isolated so policy-selection logic can evolve
        without changing workflow code.
        """

        policy = db.query(Policy).filter(
            Policy.policy_code==PolicyResolver.DEFAULT_POLICY_CODE,
            Policy.is_active.is_(True),
        ).first()


        if policy is None:
            raise ValueError(
                "No active procurement policy is available"
            )

        return policy