import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai.agents.graph import ProcureOpsGraph
from app.ai.schemas.memory import MemoryExtraction
from app.core.database import SessionLocal
from app.models.memory.conversation_memory import ConversationMemory


USER_1_ID = 910001
USER_2_ID = 910002


@pytest.mark.asyncio
async def test_long_term_memory_graph_end_to_end():
    """
    Graph-level E2E test for long-term memory.

    Verifies:

    1. A user sends a query through the real LangGraph.
    2. The long-term memory node extracts and persists memory
       into the real PostgreSQL database.
    3. A new conversation thread for the same user retrieves
       the previously stored memory.
    4. A different user cannot retrieve that memory.

    LLM-dependent nodes are mocked so the test does not require
    a real Groq API call.

    The following remain real:
    - LangGraph
    - PostgreSQL
    - Long-term memory service
    - Memory retrieval node
    - Long-term memory node
    """

    graph = ProcureOpsGraph.build_graph()

    db = SessionLocal()

    try:
        # ==========================================================
        # CLEANUP PREVIOUS TEST DATA
        # ==========================================================

        db.query(ConversationMemory).filter(
            ConversationMemory.user_id.in_(
                [USER_1_ID, USER_2_ID]
            )
        ).delete(
            synchronize_session=False
        )

        db.commit()

        # ==========================================================
        # MOCK INTENT CLASSIFICATION
        # ==========================================================

        mock_intent = MagicMock()

        mock_intent.intent = "GENERAL_PROCUREMENT"
        mock_intent.confidence = 0.95

        # ==========================================================
        # MEMORY EXTRACTION RESULT
        # ==========================================================

        memory_extraction = MemoryExtraction(
            should_remember=True,
            memory_type="PREFERENCE",
            content=(
                "User prefers vendors with shorter delivery times."
            ),
        )

        # ==========================================================
        # NO-MEMORY EXTRACTION RESULT
        #
        # Used for subsequent queries so the graph does not
        # create another long-term memory.
        # ==========================================================

        no_memory_extraction = MemoryExtraction(
            should_remember=False,
            memory_type="GENERAL",
            content="",
        )

        # ==========================================================
        # GENERAL NODE RESPONSE
        # ==========================================================

        mock_general_response = MagicMock()

        mock_general_response.content = (
            "I will keep your preference for shorter delivery "
            "times in mind."
        )

        # ==========================================================
        # FIRST CONVERSATION
        #
        # User 1 creates a long-term memory.
        # ==========================================================

        with patch(
            "app.ai.services.intent_classification_service."
            "IntentClassificationService.classify",
            return_value=mock_intent,
        ), patch(
            "app.ai.agents.nodes.general_node.get_llm",
        ) as mock_general_get_llm, patch(
            "app.ai.memory.memory_extractor.get_llm",
        ) as mock_memory_get_llm:

            # ------------------------------------------------------
            # Mock LLM used by general_node
            # ------------------------------------------------------

            mock_general_llm = MagicMock()

            mock_general_llm.invoke.return_value = (
                mock_general_response
            )

            mock_general_get_llm.return_value = (
                mock_general_llm
            )

            # ------------------------------------------------------
            # Mock LLM used by MemoryExtractor
            # ------------------------------------------------------

            mock_memory_llm = MagicMock()

            mock_structured_llm = MagicMock()

            mock_structured_llm.ainvoke = AsyncMock(
                return_value=memory_extraction
            )

            mock_memory_llm.with_structured_output.return_value = (
                mock_structured_llm
            )

            mock_memory_get_llm.return_value = (
                mock_memory_llm
            )

            # ------------------------------------------------------
            # Invoke REAL LangGraph
            # ------------------------------------------------------

            result_1 = await graph.ainvoke(
                {
                    "user_id": USER_1_ID,
                    "user_query": (
                        "Remember that I prefer vendors "
                        "with shorter delivery times."
                    ),
                },
                config={
                    "configurable": {
                        "thread_id": (
                            "memory-e2e-user-1-thread-1"
                        )
                    }
                },
            )

        # ==========================================================
        # VERIFY GRAPH EXECUTION
        # ==========================================================

        assert result_1 is not None

        assert result_1.get("response") is not None

        # ==========================================================
        # VERIFY MEMORY WAS PERSISTED IN REAL POSTGRESQL
        # ==========================================================

        saved_memory = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.user_id == USER_1_ID,
                ConversationMemory.content
                == (
                    "User prefers vendors with shorter "
                    "delivery times."
                ),
            )
            .first()
        )

        assert saved_memory is not None

        assert saved_memory.user_id == USER_1_ID

        assert saved_memory.memory_type == "PREFERENCE"

        assert saved_memory.source == "AGENT"

        # ==========================================================
        # SECOND CONVERSATION
        #
        # Same user.
        # Different thread.
        #
        # This is the important long-term-memory test.
        # ==========================================================

        with patch(
            "app.ai.services.intent_classification_service."
            "IntentClassificationService.classify",
            return_value=mock_intent,
        ), patch(
            "app.ai.agents.nodes.general_node.get_llm",
        ) as mock_general_get_llm, patch(
            "app.ai.memory.memory_extractor.get_llm",
        ) as mock_memory_get_llm:

            # ------------------------------------------------------
            # Mock general response
            # ------------------------------------------------------

            mock_general_llm = MagicMock()

            mock_general_llm.invoke.return_value = (
                mock_general_response
            )

            mock_general_get_llm.return_value = (
                mock_general_llm
            )

            # ------------------------------------------------------
            # Prevent another memory from being saved
            # ------------------------------------------------------

            mock_memory_llm = MagicMock()

            mock_structured_llm = MagicMock()

            mock_structured_llm.ainvoke = AsyncMock(
                return_value=no_memory_extraction
            )

            mock_memory_llm.with_structured_output.return_value = (
                mock_structured_llm
            )

            mock_memory_get_llm.return_value = (
                mock_memory_llm
            )

            # ------------------------------------------------------
            # Invoke REAL LangGraph with a NEW thread
            # ------------------------------------------------------

            result_2 = await graph.ainvoke(
                {
                    "user_id": USER_1_ID,
                    "user_query": (
                        "What do you know about my preferences?"
                    ),
                },
                config={
                    "configurable": {
                        "thread_id": (
                            "memory-e2e-user-1-thread-2"
                        )
                    }
                },
            )

        # ==========================================================
        # VERIFY LONG-TERM MEMORY WAS RETRIEVED
        # ==========================================================

        retrieved_memories = result_2.get(
            "retrieved_memories",
            []
        )

        assert any(
            memory["content"]
            == (
                "User prefers vendors with shorter "
                "delivery times."
            )
            for memory in retrieved_memories
        )

        # ==========================================================
        # THIRD CONVERSATION
        #
        # Different user.
        #
        # User 2 must NOT receive User 1's memory.
        # ==========================================================

        with patch(
            "app.ai.services.intent_classification_service."
            "IntentClassificationService.classify",
            return_value=mock_intent,
        ), patch(
            "app.ai.agents.nodes.general_node.get_llm",
        ) as mock_general_get_llm, patch(
            "app.ai.memory.memory_extractor.get_llm",
        ) as mock_memory_get_llm:

            # ------------------------------------------------------
            # Mock general response
            # ------------------------------------------------------

            mock_general_llm = MagicMock()

            mock_general_llm.invoke.return_value = (
                mock_general_response
            )

            mock_general_get_llm.return_value = (
                mock_general_llm
            )

            # ------------------------------------------------------
            # No new memory
            # ------------------------------------------------------

            mock_memory_llm = MagicMock()

            mock_structured_llm = MagicMock()

            mock_structured_llm.ainvoke = AsyncMock(
                return_value=no_memory_extraction
            )

            mock_memory_llm.with_structured_output.return_value = (
                mock_structured_llm
            )

            mock_memory_get_llm.return_value = (
                mock_memory_llm
            )

            # ------------------------------------------------------
            # Invoke REAL LangGraph for User 2
            # ------------------------------------------------------

            result_3 = await graph.ainvoke(
                {
                    "user_id": USER_2_ID,
                    "user_query": (
                        "What do you know about my preferences?"
                    ),
                },
                config={
                    "configurable": {
                        "thread_id": (
                            "memory-e2e-user-2-thread-1"
                        )
                    }
                },
            )

        # ==========================================================
        # VERIFY USER ISOLATION
        # ==========================================================

        retrieved_memories_user_2 = result_3.get(
            "retrieved_memories",
            []
        )

        assert not any(
            memory["content"]
            == (
                "User prefers vendors with shorter "
                "delivery times."
            )
            for memory in retrieved_memories_user_2
        )

    finally:
        # ==========================================================
        # CLEANUP TEST DATA
        # ==========================================================

        db.query(ConversationMemory).filter(
            ConversationMemory.user_id.in_(
                [USER_1_ID, USER_2_ID]
            )
        ).delete(
            synchronize_session=False
        )

        db.commit()

        db.close()