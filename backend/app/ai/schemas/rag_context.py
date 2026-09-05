from pydantic import BaseModel, Field


class RAGSource(BaseModel):
    document_name: str
    chunk_number: int
    score: float


class RAGContext(BaseModel):
    context: str
    sources: list[RAGSource] = Field(
        default_factory=list,
    )