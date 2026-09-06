"""add challenge accepted answers

Revision ID: 20260906_0002
Revises: 20260906_0001
Create Date: 2026-09-06

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260906_0002"
down_revision: str | None = "20260906_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column("accepted_answers", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("challenges", "accepted_answers")
