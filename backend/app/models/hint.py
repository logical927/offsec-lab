from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Hint(Base):
    __tablename__ = "hints"
    __table_args__ = (
        UniqueConstraint("challenge_id", "level", name="uq_hints_challenge_level"),
        CheckConstraint("level BETWEEN 1 AND 3", name="ck_hints_level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
