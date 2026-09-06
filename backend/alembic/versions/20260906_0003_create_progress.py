"""create progress

Revision ID: 20260906_0003
Revises: 20260906_0002
Create Date: 2026-09-06

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260906_0003"
down_revision: str | None = "20260906_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_challenges_mission_id_id",
        "challenges",
        ["mission_id", "id"],
    )
    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('LOCKED', 'AVAILABLE', 'COMPLETED')",
            name="ck_progress_status",
        ),
        sa.ForeignKeyConstraint(
            ["mission_id", "challenge_id"],
            ["challenges.mission_id", "challenges.id"],
            name="fk_progress_mission_challenge",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_progress")),
        sa.UniqueConstraint(
            "mission_id",
            "challenge_id",
            name="uq_progress_mission_id_challenge_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("progress")
    op.drop_constraint(
        "uq_challenges_mission_id_id",
        "challenges",
        type_="unique",
    )
