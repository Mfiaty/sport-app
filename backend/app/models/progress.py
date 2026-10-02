from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserProgress(Base):
    """Progression d'une utilisatrice, une ligne par sport."""

    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "sport_id", name="uq_progress_user_sport"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    level: Mapped[int] = mapped_column(Integer, default=1)
    # Ne fait que monter : réviser une ancienne notion ne la fait jamais baisser
    highest_notion_position: Mapped[int] = mapped_column(Integer, default=1)
    # La notion ouverte en ce moment (peut être une ancienne, en révision)
    current_notion_id: Mapped[int | None] = mapped_column(
        ForeignKey("notions.id"), nullable=True
    )
    rank: Mapped[str] = mapped_column(String(50), default="Poussin")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class NotionAttempt(Base):
    """Historique de chaque tentative de quiz sur une notion."""

    __tablename__ = "notion_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    notion_id: Mapped[int] = mapped_column(ForeignKey("notions.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    passed: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )