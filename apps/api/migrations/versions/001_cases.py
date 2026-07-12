"""create cases table"""
from alembic import op
import sqlalchemy as sa

revision = "001_cases"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("customer_token", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cases_customer_token", "cases", ["customer_token"], unique=True)
    op.create_index("ix_cases_status", "cases", ["status"])


def downgrade() -> None:
    op.drop_index("ix_cases_status", table_name="cases")
    op.drop_index("ix_cases_customer_token", table_name="cases")
    op.drop_table("cases")
