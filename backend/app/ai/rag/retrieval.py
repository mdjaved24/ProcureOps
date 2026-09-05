from fastapi import HTTPException, status
from langsmith import traceable

from app.ai.rag.vector_store import VectorStoreService


class RetrievalService:

    @staticmethod
    @traceable(name="rag_retrieval")
    def retrieve(
        user_query: str,
        top_k: int,
    ):
        if not user_query or not user_query.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Query cannot be empty",
            )

        vector_store = VectorStoreService.get_vector_store()

        results = vector_store.similarity_search_with_score(
            query=user_query,
            k=top_k,
        )

        return results