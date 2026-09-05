import pytest
from unittest.mock import MagicMock, patch

from app.ai.rag.rag_answer_service import RAGAnswerService
from app.ai.schemas.rag_context import RAGContext


def create_rag_context():
    return RAGContext(
        context=(
            "Purchase orders above ₹1,00,000 require manager approval."
        ),
        sources=[
            {
                "document_name": "procurement_policy.pdf",
                "chunk_number": 5,
                "score": 0.92,
            }
        ],
    )


def test_generate_answer_without_memory():

    rag_context = create_rag_context()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Purchase orders above ₹1,00,000 require manager approval."
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm

        result = RAGAnswerService.generate_answer(
            user_query="When is manager approval required?",
            rag_context=rag_context,
        )

    assert result.answer == (
        "Purchase orders above ₹1,00,000 require manager approval."
    )

    assert result.sources == rag_context.sources

    mock_llm.invoke.assert_called_once()


def test_generate_answer_with_memory():

    rag_context = create_rag_context()

    retrieved_memories = [
        {
            "memory_type": "PREFERENCE",
            "content": "User prefers concise explanations.",
            "source": "AGENT",
        },
        {
            "memory_type": "FACT",
            "content": (
                "User frequently works with procurement "
                "approval workflows."
            ),
            "source": "AGENT",
        },
    ]

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Manager approval is required for purchase orders "
        "above ₹1,00,000."
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm

        result = RAGAnswerService.generate_answer(
            user_query="When is manager approval required?",
            rag_context=rag_context,
            retrieved_memories=retrieved_memories,
        )

    assert result.answer == (
        "Manager approval is required for purchase orders "
        "above ₹1,00,000."
    )

    assert result.sources == rag_context.sources

    mock_llm.invoke.assert_called_once()

    messages = mock_llm.invoke.call_args.args[0]

    user_message = messages[1].content

    assert "RELEVANT LONG-TERM USER MEMORY" in user_message

    assert "User prefers concise explanations." in user_message

    assert (
        "User frequently works with procurement "
        "approval workflows."
        in user_message
    )


def test_generate_answer_memory_defaults_to_empty():

    rag_context = create_rag_context()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Manager approval is required."
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm

        result = RAGAnswerService.generate_answer(
            user_query="When is approval required?",
            rag_context=rag_context,
            retrieved_memories=None,
        )

    assert result.answer == (
        "Manager approval is required."
    )

    messages = mock_llm.invoke.call_args.args[0]

    user_message = messages[1].content

    assert "RELEVANT LONG-TERM USER MEMORY" in user_message

    mock_llm.invoke.assert_called_once()


def test_generate_answer_rejects_empty_query():

    rag_context = create_rag_context()

    with pytest.raises(
        ValueError,
        match="User query cannot be empty",
    ):
        RAGAnswerService.generate_answer(
            user_query="",
            rag_context=rag_context,
        )


def test_generate_answer_rejects_whitespace_query():

    rag_context = create_rag_context()

    with pytest.raises(
        ValueError,
        match="User query cannot be empty",
    ):
        RAGAnswerService.generate_answer(
            user_query="   ",
            rag_context=rag_context,
        )


def test_generate_answer_with_empty_rag_context():

    rag_context = RAGContext(
        context="",
        sources=[],
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        result = RAGAnswerService.generate_answer(
            user_query="What is the procurement policy?",
            rag_context=rag_context,
        )

    assert result.answer == (
        "I could not find relevant information "
        "in the procurement knowledge base to "
        "answer this question."
    )

    assert result.sources == []

    mock_get_llm.assert_not_called()


def test_generate_answer_preserves_sources():

    rag_context = RAGContext(
        context="RFQs require vendor quotations.",
        sources=[
            {
                "document_name": "rfq_policy.pdf",
                "chunk_number": 10,
                "score": 0.95,
            },
            {
                "document_name": "vendor_policy.pdf",
                "chunk_number": 3,
                "score": 0.88,
            },
        ],
    )

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "RFQs require vendor quotations."
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm

        result = RAGAnswerService.generate_answer(
            user_query="What is required for an RFQ?",
            rag_context=rag_context,
        )

    assert result.sources == rag_context.sources


def test_memory_and_rag_context_are_both_sent_to_llm():

    rag_context = RAGContext(
        context=(
            "Purchase orders above ₹1,00,000 require manager approval."
        ),
        sources=[
            {
                "document_name": "procurement_policy.pdf",
                "chunk_number": 5,
                "score": 0.92,
            }
        ],
    )

    retrieved_memories = [
        {
            "memory_type": "PREFERENCE",
            "content": "User prefers concise responses.",
            "source": "AGENT",
        }
    ]

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Manager approval is required above ₹1,00,000."
    )

    with patch(
        "app.ai.rag.rag_answer_service.get_llm"
    ) as mock_get_llm:

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm

        RAGAnswerService.generate_answer(
            user_query="When is manager approval required?",
            rag_context=rag_context,
            retrieved_memories=retrieved_memories,
        )

    messages = mock_llm.invoke.call_args.args[0]

    system_message = messages[0].content
    user_message = messages[1].content

    # RAG context is passed
    assert (
        "Purchase orders above ₹1,00,000 require manager approval."
        in user_message
    )

    # Long-term memory is passed
    assert "User prefers concise responses." in user_message

    # System prompt establishes knowledge base authority
    assert "knowledge base" in system_message

    # Memory cannot override RAG
    assert "must NOT override the knowledge base" in system_message