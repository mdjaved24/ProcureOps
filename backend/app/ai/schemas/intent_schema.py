from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IntentClassification(str, Enum):

    GENERAL_PROCUREMENT = "GENERAL_PROCUREMENT"

    PURCHASE_REQUEST = "PURCHASE_REQUEST"

    RFQ = "RFQ"

    QUOTATION = "QUOTATION"

    VENDOR = "VENDOR"

    POLICY = "POLICY"


class IntentModel(BaseModel):

    intent: IntentClassification

    confidence: Optional[float] = Field(
        ge=0.0,
        le=1.0,
    )

    reason: Optional[str] = Field(
        default=None,
        description="Brief reason for the classification"
    )