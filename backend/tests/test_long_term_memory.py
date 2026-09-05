import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai.agents.nodes.long_term_memory_node import (
    long_term_memory_node,
)
from app.ai.schemas.memory import MemoryExtraction


@pytest.mark.asyncio
async def test_long_term_memory_saves_memory():

    state = {
        "user_query": (
            "I prefer vendors with shorter delivery times."
        ),
        "response": (
            "I will consider your preference "
            "for shorter delivery times."
        ),
    }

    extraction = MemoryExtraction(
        should_remember=True,
        memory_type="PREFERENCE",
        content=(
            "User prefers vendors with shorter "
            "delivery times."
        ),
    )

    with patch(
        "app.ai.agents.nodes.long_term_memory_node.MemoryExtractor.extract",
        new=AsyncMock(return_value=extraction),
    ), patch(
        "app.ai.agents.nodes.long_term_memory_node.SessionLocal"
    ) as mock_session_local, patch(
        "app.ai.agents.nodes.long_term_memory_node.LongTermMemoryService.save_memory"
    ) as mock_save_memory:

        mock_db = MagicMock()

        mock_session_local.return_value = mock_db

        result = await long_term_memory_node(state)

        mock_save_memory.assert_called_once_with(
            db=mock_db,
            content=(
                "User prefers vendors with shorter "
                "delivery times."
            ),
            memory_type="PREFERENCE",
            source="AGENT",
        )

        mock_db.close.assert_called_once()

        assert result["long_term_memory"]["saved"] is True
        assert (
            result["long_term_memory"]["memory_type"]
            == "PREFERENCE"
        )


@pytest.mark.asyncio
async def test_long_term_memory_does_not_save_when_not_required():

    state = {
        "user_query": "Show quotations for RFQ-000013",
        "response": "Here are the quotations.",
    }

    extraction = MemoryExtraction(
        should_remember=False,
        memory_type="GENERAL",
        content="",
    )

    with patch(
        "app.ai.agents.nodes.long_term_memory_node.MemoryExtractor.extract",
        new=AsyncMock(return_value=extraction),
    ), patch(
        "app.ai.agents.nodes.long_term_memory_node.LongTermMemoryService.save_memory"
    ) as mock_save_memory:

        result = await long_term_memory_node(state)

        mock_save_memory.assert_not_called()

        assert result == {}


@pytest.mark.asyncio
async def test_long_term_memory_does_not_save_empty_content():

    state = {
        "user_query": "I prefer vendors with faster delivery.",
        "response": "Understood.",
    }

    extraction = MemoryExtraction(
        should_remember=True,
        memory_type="PREFERENCE",
        content="   ",
    )

    with patch(
        "app.ai.agents.nodes.long_term_memory_node.MemoryExtractor.extract",
        new=AsyncMock(return_value=extraction),
    ), patch(
        "app.ai.agents.nodes.long_term_memory_node.LongTermMemoryService.save_memory"
    ) as mock_save_memory:

        result = await long_term_memory_node(state)

        mock_save_memory.assert_not_called()

        assert result == {}


@pytest.mark.asyncio
async def test_long_term_memory_requires_query_and_response():

    state = {
        "user_query": "Hello",
    }

    with patch(
        "app.ai.agents.nodes.long_term_memory_node.MemoryExtractor.extract",
        new=AsyncMock(),
    ) as mock_extract:

        result = await long_term_memory_node(state)

        mock_extract.assert_not_awaited()

        assert result == {}