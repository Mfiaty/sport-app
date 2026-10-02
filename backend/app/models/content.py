from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)  # ex. "football"
    name: Mapped[str] = mapped_column(String(100))

    notions: Mapped[list["Notion"]] = relationship(
        back_populates="sport", order_by="Notion.position"
    )


class Notion(Base):
    __tablename__ = "notions"
    __table_args__ = (
        UniqueConstraint("sport_id", "level", "position", name="uq_notion_place"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    level: Mapped[int] = mapped_column(Integer, default=1)  # 1 = débutant
    position: Mapped[int] = mapped_column(Integer)  # ordre dans le parcours
    title: Mapped[str] = mapped_column(String(200))

    sport: Mapped["Sport"] = relationship(back_populates="notions")
    screens: Mapped[list["LessonScreen"]] = relationship(
        back_populates="notion",
        order_by="LessonScreen.position",
        cascade="all, delete-orphan",
    )
    questions: Mapped[list["Question"]] = relationship(
        back_populates="notion", cascade="all, delete-orphan"
    )


class LessonScreen(Base):
    __tablename__ = "lesson_screens"
    __table_args__ = (
        UniqueConstraint("notion_id", "position", name="uq_screen_place"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    notion_id: Mapped[int] = mapped_column(ForeignKey("notions.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_fun_fact: Mapped[bool] = mapped_column(Boolean, default=False)  # « Le savais-tu ? »

    notion: Mapped["Notion"] = relationship(back_populates="screens")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("notion_id", "pair_number", "variant", name="uq_question_slot"),
        CheckConstraint("pair_number BETWEEN 1 AND 5", name="ck_pair_number"),
        CheckConstraint("variant IN ('a', 'b')", name="ck_variant"),
        CheckConstraint("difficulty BETWEEN 1 AND 10", name="ck_difficulty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    notion_id: Mapped[int] = mapped_column(ForeignKey("notions.id", ondelete="CASCADE"))
    pair_number: Mapped[int] = mapped_column(Integer)  # 1 à 5
    variant: Mapped[str] = mapped_column(String(1))  # "a" ou "b"
    difficulty: Mapped[int] = mapped_column(Integer)
    statement: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)

    notion: Mapped["Notion"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    why_wrong: Mapped[str | None] = mapped_column(Text, nullable=True)  # « Pourquoi pas celle-ci »

    question: Mapped["Question"] = relationship(back_populates="answers")