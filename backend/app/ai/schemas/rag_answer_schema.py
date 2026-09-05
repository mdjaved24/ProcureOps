from pydantic import BaseModel, Field
from app.ai.schemas.rag_context import RAGSource


class RAGAnswer(BaseModel):
    answer: str
    sources: list[RAGSource] = Field(
        default_factory=list,
    )