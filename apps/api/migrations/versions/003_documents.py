"""create documents table"""
from alembic import op
import sqlalchemy as sa

revision = "003_documents"
down_revision = "002_registration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("documents", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("material_type", sa.String(80), nullable=False), sa.Column("person_role", sa.String(40), nullable=False), sa.Column("original_name", sa.String(255), nullable=False), sa.Column("content_type", sa.String(100), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("storage_key", sa.String(300), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_documents_case_id", "documents", ["case_id"])
    op.create_index("ix_documents_material_type", "documents", ["material_type"])


def downgrade() -> None:
    op.drop_table("documents")
