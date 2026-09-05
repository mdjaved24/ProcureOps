from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class TextSplitterService:

    @staticmethod
    def split_documents(
        documents: list[Document],
    ) -> list[Document]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
        )

        chunks = splitter.split_documents(
            documents=documents,
        )

        for index, chunk in enumerate(chunks, start=1):
            source = chunk.metadata.get(
                "source",
                "",
            )

            chunk.metadata["document_name"] = Path(source).name

            chunk.metadata["chunk_number"] = index

        return chunks
