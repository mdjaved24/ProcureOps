from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


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


class PendingApprovalResponse(BaseModel):

    approval_id: int
    approval_status: str

    approval_step_id: int
    sequence: int
    required_role: str
    step_status: str

    purchase_request_id: int
    request_number: str
    title: str
    estimated_amount: Decimal
    currency: str
    purchase_request_status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ApprovalStepResponse(BaseModel):
    id: int
    required_role: str
    sequence: int
    status: str

    decided_by: int | None
    decision_at: datetime | None
    decision_comments: str | None

    class Config:
        from_attributes = True



class ApprovalResponse(BaseModel):
    id: int

    purchase_request_id: int

    status: str
    approval_type: str

    created_at: datetime
    updated_at: datetime

    steps: list[ApprovalStepResponse]

    class Config:
        from_attributes = True