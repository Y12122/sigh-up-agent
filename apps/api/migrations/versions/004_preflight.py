"""create preflight tables"""
from alembic import op
import sqlalchemy as sa

revision = "004_preflight"
down_revision = "003_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("preflight_jobs", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("document_id", sa.Uuid(), nullable=False), sa.Column("provider", sa.String(80), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("retryable", sa.Boolean(), nullable=False), sa.Column("error_code", sa.String(80)), sa.Column("error_message", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_preflight_jobs_document_id", "preflight_jobs", ["document_id"])
    op.create_index("ix_preflight_jobs_status", "preflight_jobs", ["status"])
    op.create_table("field_candidates", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("job_id", sa.Uuid(), sa.ForeignKey("preflight_jobs.id", ondelete="CASCADE"), nullable=False), sa.Column("provider", sa.String(80), nullable=False), sa.Column("field_path", sa.String(240), nullable=False), sa.Column("value", sa.Text(), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("document_id", sa.Uuid(), nullable=False), sa.Column("page", sa.Integer(), nullable=False))
    op.create_index("ix_field_candidates_job_id", "field_candidates", ["job_id"])
    op.create_index("ix_field_candidates_field_path", "field_candidates", ["field_path"])
    op.create_table("review_findings", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("job_id", sa.Uuid(), sa.ForeignKey("preflight_jobs.id", ondelete="CASCADE"), nullable=False), sa.Column("code", sa.String(100), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("message", sa.Text(), nullable=False))
    op.create_index("ix_review_findings_job_id", "review_findings", ["job_id"])
    op.create_index("ix_review_findings_code", "review_findings", ["code"])


def downgrade() -> None:
    op.drop_table("review_findings")
    op.drop_table("field_candidates")
    op.drop_table("preflight_jobs")
