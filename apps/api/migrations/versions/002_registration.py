"""create registration and audit tables"""
from alembic import op
import sqlalchemy as sa

revision = "002_registration"
down_revision = "001_cases"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("companies", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False), sa.Column("name_zh", sa.String(200), nullable=False), sa.Column("name_en", sa.String(200), nullable=False), sa.Column("business_scope", sa.String(30), nullable=False), sa.Column("registered_capital", sa.Numeric(18, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False))
    op.create_table("registration_profiles", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False), sa.Column("registered_address", sa.Text(), nullable=False), sa.Column("contact_name", sa.String(120), nullable=False), sa.Column("contact_phone", sa.String(40), nullable=False))
    op.create_table("persons", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(30), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("document_type", sa.String(40)), sa.Column("document_number", sa.String(120)), sa.Column("phone", sa.String(40)), sa.Column("email", sa.String(200)))
    op.create_index("ix_persons_case_id", "persons", ["case_id"])
    op.create_index("ix_persons_role", "persons", ["role"])
    op.create_table("shareholders", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("position", sa.Integer(), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("share_percentage", sa.Numeric(5, 2), nullable=False), sa.UniqueConstraint("case_id", "position"))
    op.create_index("ix_shareholders_case_id", "shareholders", ["case_id"])
    op.create_table("field_versions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("field_path", sa.String(240), nullable=False), sa.Column("value", sa.JSON(), nullable=False), sa.Column("previous_value", sa.JSON()), sa.Column("source", sa.String(40), nullable=False), sa.Column("actor_id", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_field_versions_case_id", "field_versions", ["case_id"])
    op.create_index("ix_field_versions_field_path", "field_versions", ["field_path"])
    op.create_table("audit_logs", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False), sa.Column("action", sa.String(100), nullable=False), sa.Column("actor_id", sa.String(120), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_audit_logs_case_id", "audit_logs", ["case_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    for table in ("audit_logs", "field_versions", "shareholders", "persons", "registration_profiles", "companies"):
        op.drop_table(table)
