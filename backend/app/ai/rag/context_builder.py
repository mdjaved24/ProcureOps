from pathlib import Path

from langchain_core.documents import Document

from app.ai.schemas.rag_context import (
    RAGContext,
    RAGSource,
)


class RAGContextBuilder:

    @staticmethod
    def build_context(
        retrieval_results: list[
            tuple[Document, float]
        ],
    ) -> RAGContext:

        # ==============================================
        # EMPTY RESULTS
        # ==============================================

        if not retrieval_results:
            return RAGContext(
                context="",
                sources=[],
            )

        context_parts: list[str] = []
        sources: list[RAGSource] = []

        # ==============================================
        # PROCESS RETRIEVAL RESULTS
        # ==============================================

        for document, score in retrieval_results:

            # ==========================================
            # DOCUMENT NAME
            # ==========================================

            document_name = (
                document.metadata.get("document_name")
                or document.metadata.get("filename")
            )

            # Fallback to filename from source path

            if not document_name:

                source_path = (
                    document.metadata.get("source")
                )

                if source_path:
                    document_name = (
                        Path(source_path).name
                    )

                else:
                    document_name = "unknown"

            # ==========================================
            # CHUNK NUMBER
            # ==========================================

            chunk_number = (
                document.metadata.get(
                    "chunk_number",
                    0,
                )
            )

            # ==========================================
            # PAGE CONTENT
            # ==========================================

            page_content = (
                document.page_content.strip()
            )

            # Skip empty chunks

            if not page_content:
                continue

            # ==========================================
            # FORMAT CONTEXT
            # ==========================================

            formatted_context = (
                f"SOURCE: {document_name}\n"
                f"CHUNK: {chunk_number}\n\n"
                f"CONTENT:\n"
                f"{page_content}"
            )

            context_parts.append(
                formatted_context
            )

            # ==========================================
            # SOURCE METADATA
            # ==========================================

            sources.append(
                RAGSource(
                    document_name=document_name,
                    chunk_number=int(chunk_number),
                    score=float(score),
                )
            )

        # ==============================================
        # BUILD FINAL CONTEXT
        # ==============================================

        context = "\n\n---\n\n".join(
            context_parts
        )

        # ==============================================
        # RETURN
        # ==============================================

        return RAGContext(
            context=context,
            sources=sources,
        )