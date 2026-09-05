from sqlalchemy.orm import Session

from app.models.memory.conversation_memory import (
    ConversationMemory,
)


class LongTermMemoryService:

    @staticmethod
    def save_memory(
        db: Session,
        content: str,
        memory_type: str = "GENERAL",
        user_id: int | None = None,
        thread_id: str | None = None,
        source: str = "AGENT",
    ) -> ConversationMemory:

        memory = ConversationMemory(
            user_id=user_id,
            thread_id=thread_id,
            memory_type=memory_type,
            content=content,
            source=source,
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    @staticmethod
    def get_memories(
        db: Session,
        user_id: int | None = None,
        thread_id: str | None = None,
        memory_type: str | None = None,
        limit: int = 20,
    ) -> list[ConversationMemory]:

        query = db.query(
            ConversationMemory
        )

        if user_id is not None:
            query = query.filter(
                ConversationMemory.user_id == user_id
            )

        if thread_id is not None:
            query = query.filter(
                ConversationMemory.thread_id == thread_id
            )

        if memory_type is not None:
            query = query.filter(
                ConversationMemory.memory_type == memory_type
            )

        return (
            query
            .order_by(
                ConversationMemory.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_memories(
        db: Session,
        user_id: int | None = None,
        limit: int = 10,
    ) -> list[ConversationMemory]:

        query = db.query(
            ConversationMemory
        )

        if user_id is not None:
            query = query.filter(
                ConversationMemory.user_id == user_id
            )

        return (
            query
            .order_by(
                ConversationMemory.created_at.desc()
            )
            .limit(limit)
            .all()
        )