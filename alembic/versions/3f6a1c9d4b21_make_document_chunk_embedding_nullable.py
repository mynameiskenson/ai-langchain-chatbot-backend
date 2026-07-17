"""make document chunk embedding nullable

Revision ID: 3f6a1c9d4b21
Revises: 2cbecc27cd20
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '3f6a1c9d4b21'
down_revision: Union[str, Sequence[str], None] = '2cbecc27cd20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Embeddings are now written by the pluggable vector store (pgvector,
    # Qdrant, Pinecone, ...) instead of always being required inline during
    # chunk creation, so the column must allow NULL.
    op.alter_column(
        'document_chunks',
        'embedding',
        existing_type=Vector(dim=768),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'document_chunks',
        'embedding',
        existing_type=Vector(dim=768),
        nullable=False,
    )
