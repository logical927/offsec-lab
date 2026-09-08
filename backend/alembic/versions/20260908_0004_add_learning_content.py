"""Add progressive hints and mission learning explanation.

Revision ID: 20260908_0004
Revises: 20260906_0003
"""
from alembic import op
import sqlalchemy as sa

revision = "20260908_0004"
down_revision = "20260906_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("missions", sa.Column("learning_explanation", sa.Text(), nullable=True))
    op.create_table(
        "hints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.UniqueConstraint("challenge_id", "level", name="uq_hints_challenge_level"),
        sa.CheckConstraint("level BETWEEN 1 AND 3", name="ck_hints_level"),
    )


def downgrade() -> None:
    op.drop_table("hints")
    op.drop_column("missions", "learning_explanation")
