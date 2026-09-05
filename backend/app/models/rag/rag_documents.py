from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.core.database import Base


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_name = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    document_path = Column(
        String(500),
        nullable=False,
    )

    content_hash = Column(
        String(64),
        nullable=False,
    )

    chunk_count = Column(
        Integer,
        nullable=False,
    )

    last_ingested_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )