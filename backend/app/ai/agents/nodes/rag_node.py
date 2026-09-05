from app.ai.agents.state import ProcureOpsState
from app.ai.rag.context_builder import RAGContextBuilder
from app.ai.rag.retrieval import RetrievalService
from app.ai.rag.rag_answer_service import RAGAnswerService


def rag_node(
    state: ProcureOpsState,
) -> dict:

    # ==============================================
    # READ STATE
    # ==============================================

    user_query = state["user_query"]

    retrieved_memories = state.get(
        "retrieved_memories",
        [],
    )

    top_k = 3

    # ==============================================
    # RETRIEVE RELEVANT DOCUMENTS
    # ==============================================

    retrieval_results = RetrievalService.retrieve(
        user_query=user_query,
        top_k=top_k,
    )

    # ==============================================
    # BUILD RAG CONTEXT
    # ==============================================

    context = RAGContextBuilder.build_context(
        retrieval_results=retrieval_results,
    )

    # ==============================================
    # GENERATE GROUNDED ANSWER
    # ==============================================

    response = RAGAnswerService.generate_answer(
        user_query=user_query,
        rag_context=context,
        retrieved_memories=retrieved_memories,
    )

    # ==============================================
    # UPDATE GRAPH STATE
    # ==============================================

    return {
        "response": response.answer,
        "sources": response.sources,
    }