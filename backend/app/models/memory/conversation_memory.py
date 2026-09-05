from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from sqlalchemy.sql import func

from app.core.database import Base


class ConversationMemory(Base):

    __tablename__ = "conversation_memories"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    thread_id = Column(
        String(255),
        nullable=True,
        index=True,
    )

    memory_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    source = Column(
        String(100),
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