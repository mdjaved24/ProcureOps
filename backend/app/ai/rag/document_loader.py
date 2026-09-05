from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    UnstructuredMarkdownLoader,
)


class DocumentLoaderService:

    @staticmethod
    def load_documents(
        file_path: str | Path,
        mode: str = "elements",
    ) -> list[Document]:

        loader = UnstructuredMarkdownLoader(
            file_path=str(file_path),
            mode=mode,
        )

        documents = loader.load()

        return documents