from enum import Enum

from pydantic import BaseModel, Field


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class ApprovalDecisionRequest(BaseModel):
    decision: ApprovalDecision

    comments: str | None = Field(
        default=None,
        max_length=2000,
    )