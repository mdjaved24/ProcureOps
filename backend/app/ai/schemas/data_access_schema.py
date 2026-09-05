from enum import Enum

from pydantic import BaseModel


class DataAccessType(str, Enum):

    KNOWLEDGE = "KNOWLEDGE"

    LIVE_DATA = "LIVE_DATA"


class DataAccessModel(BaseModel):

    data_access_type: DataAccessType

    confidence: float