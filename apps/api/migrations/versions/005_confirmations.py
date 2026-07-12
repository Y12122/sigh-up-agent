"""create confirmations table"""
from alembic import op
import sqlalchemy as sa

revision = "005_confirmations"
down_revision = "004_preflight"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("confirmations", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("snapshot", sa.JSON(), nullable=False), sa.Column("snapshot_hash", sa.String(64), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("docx_storage_key", sa.String(300), nullable=False), sa.Column("pdf_storage_key", sa.String(300), nullable=False), sa.Column("created_by", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("confirmed_at", sa.DateTime(timezone=True)), sa.Column("invalidated_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("case_id", "version"))
    op.create_index("ix_confirmations_case_id", "confirmations", ["case_id"])
    op.create_index("ix_confirmations_snapshot_hash", "confirmations", ["snapshot_hash"])
    op.create_index("ix_confirmations_status", "confirmations", ["status"])


def downgrade() -> None:
    op.drop_table("confirmations")
