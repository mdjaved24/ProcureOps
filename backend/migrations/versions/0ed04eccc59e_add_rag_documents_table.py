"""Add RAG documents table

Revision ID: 0ed04eccc59e
Revises: 8b8c3c8bf23c
Create Date: 2026-09-01 14:51:20.934785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ed04eccc59e'
down_revision: Union[str, Sequence[str], None] = '8b8c3c8bf23c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create rag_documents table."""
    op.create_table(
        'rag_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_path', sa.String(length=500), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.Column('last_ingested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_name', name='uq_rag_documents_document_name'),
    )
    op.create_index(op.f('ix_rag_documents_document_name'), 'rag_documents', ['document_name'], unique=True)
    op.create_index(op.f('ix_rag_documents_id'), 'rag_documents', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop rag_documents table."""
    op.drop_index(op.f('ix_rag_documents_document_name'), table_name='rag_documents')
    op.drop_index(op.f('ix_rag_documents_id'), table_name='rag_documents')
    op.drop_table('rag_documents')