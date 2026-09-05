from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.rag.rag_documents import RAGDocument

from app.ai.rag.document_hash_service import DocumentHashService
from app.ai.rag.document_loader import DocumentLoaderService
from app.ai.rag.embeddings import get_embeddings
from app.ai.rag.vector_store import VectorStoreService
from app.ai.rag.text_splitter import TextSplitterService



class IngestionService:

    @staticmethod
    def ingest_knowledge_base(db:Session)->dict:

        # ==================================================
        # KNOWLEDGE BASE DIRECTORY
        # ==================================================

        base_dir = Path(__file__).resolve().parents[3]

        knowledge_base_dir = (
            base_dir
            / "app"
            / "ai"
            / "knowledge_base"
        )

        if not knowledge_base_dir.exists():
            raise FileNotFoundError(
                f"Knowledge base directory not found: "
                f"{knowledge_base_dir}"
            )

        # ==================================================
        # FIND MARKDOWN FILES
        # ==================================================

        markdown_files = sorted(
            knowledge_base_dir.glob(
                "*.md"
            )
        )

        # ==================================================
        # GET VECTOR STORE
        # ==================================================

        vector_store = VectorStoreService.get_vector_store()

        # ==================================================
        # INGESTION SUMMARY
        # ==================================================

        summary = {
            "new_documents": 0,
            "changed_documents": 0,
            "unchanged_documents": 0,
            "deleted_documents": 0,
            "chunks_added": 0,
        }

        # Track current files for deletion detection

        current_document_names = set()

        # ==================================================
        # PROCESS CURRENT DOCUMENTS
        # ==================================================

        for file_path in markdown_files:
            document_name = file_path.name
            current_document_names.add(document_name)

            # ----------------------------------------------
            # CALCULATE HASH
            # ----------------------------------------------

            file_hash = DocumentHashService.calculate_file_hash(file_path=file_path)

            # ----------------------------------------------
            # FIND EXISTING METADATA
            # ----------------------------------------------
            existing_document = db.query(RAGDocument).filter(
                RAGDocument.document_name==document_name
            ).first()

            # ----------------------------------------------
            # UNCHANGED DOCUMENT
            # ----------------------------------------------

            if existing_document and existing_document.content_hash==file_hash:
                summary["unchanged_documents"] += 1

                continue

            # ----------------------------------------------
            # CHANGED DOCUMENT
            # ----------------------------------------------

            if existing_document:
                vector_store.delete(
                    where={
                        "document_name":document_name
                    }
                )

                summary["changed_documents"] += 1

            # ----------------------------------------------
            # NEW DOCUMENT
            # ----------------------------------------------

            else:
                summary["new_documents"] += 1

            # ==================================================
            # LOAD DOCUMENT
            # ==================================================

            documents = DocumentLoaderService.load_documents(
                file_path=file_path,
                mode="single",
                )

            # ==================================================
            # SPLIT DOCUMENT
            # ==================================================

            chunks = TextSplitterService.split_documents(documents=documents)

            # ==================================================
            # PREPARE CHUNK METADATA + IDS
            # ==================================================
            chunk_ids = []

            for chunk in chunks:
                chunk_number = chunk.metadata["chunk_number"]
                chunk.metadata["document_name"] = document_name
                chunk.metadata["document_hash"] = file_hash
                chunk_id = (
                    f"{document_name}"
                    f"::{chunk_number}"
                )

                chunk_ids.append(chunk_id)

            # ==================================================
            # ADD TO CHROMADB
            # ==================================================
            vector_store.add_documents(
                documents=chunks,
                ids=chunk_ids
            )

            # ==================================================
            # CREATE OR UPDATE DATABASE METADATA
            # ==================================================

            if existing_document:
                existing_document.document_path = str(file_path)
                existing_document.content_hash = file_hash
                existing_document.chunk_count = len(chunks)
                existing_document.last_ingested_at = datetime.now().astimezone()

            else:
                rag_document = RAGDocument(
                    document_name=document_name,
                    document_path = str(file_path),
                    content_hash = file_hash,
                    chunk_count = len(chunks),
                    last_ingested_at = datetime.now().astimezone()
                )

                db.add(rag_document)

            summary["chunks_added"]+=len(chunks)


        # ==================================================
        # DETECT DELETED DOCUMENTS
        # ==================================================
        database_documents = db.query(RAGDocument).all()

        for document in database_documents:
            if document.document_name not in current_document_names:
                # Delete Chroma chunks
                vector_store.delete(
                    where={
                        "document_name":
                        document.document_name
                    }
                )

                # Delete metadata record
                db.delete(document)

                summary["deleted_documents"] += 1

        # ==================================================
        # COMMIT DATABASE CHANGES
        # ==================================================

        try:

            db.commit()

        except Exception:

            db.rollback()

            raise

        return summary

