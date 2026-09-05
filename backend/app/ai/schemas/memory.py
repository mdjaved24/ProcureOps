from pydantic import BaseModel, Field


class MemoryExtraction(BaseModel):
    should_remember: bool = Field(
        description="Whether this information should be stored as long-term memory."
    )

    memory_type: str = Field(
        default="GENERAL",
        description=(
            "Memory category such as PREFERENCE, "
            "FACT, or GENERAL."
        ),
    )

    content: str = Field(
        default="",
        description="Concise piece of information worth remembering.",
    )