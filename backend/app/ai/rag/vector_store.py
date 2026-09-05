import os
from functools import lru_cache
from pathlib import Path
from app.core.config import settings
from langchain_chroma import Chroma

from app.ai.rag.embeddings import get_embeddings


class VectorStoreService:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_vector_store()->Chroma:

        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        collection_name = settings.CHROMA_COLLECTION_NAME

        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True,
        )


        # Embeddings model
        embeddings = get_embeddings()

        vector_store = Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=embeddings
        )


        return vector_store
    