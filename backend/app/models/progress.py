from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        UniqueConstraint(
            "mission_id",
            "challenge_id",
            name="uq_progress_mission_id_challenge_id",
        ),
        CheckConstraint(
            "status IN ('LOCKED', 'AVAILABLE', 'COMPLETED')",
            name="ck_progress_status",
        ),
        # Keep mission_id consistent with the challenge's owning mission.
        ForeignKeyConstraint(
            ["mission_id", "challenge_id"],
            ["challenges.mission_id", "challenges.id"],
            name="fk_progress_mission_challenge",
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)
    challenge_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
