from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Notion, Question, Sport


def list_notions(db: Session, sport_slug: str, level: int) -> list[Notion]:
    stmt = (
        select(Notion)
        .join(Sport)
        .where(Sport.slug == sport_slug, Notion.level == level)
        .order_by(Notion.position)
    )
    return list(db.scalars(stmt).all())


def get_notion_with_screens(db: Session, notion_id: int) -> Notion | None:
    stmt = (
        select(Notion)
        .where(Notion.id == notion_id)
        .options(selectinload(Notion.screens))
    )
    return db.scalar(stmt)


def get_questions_with_answers(db: Session, notion_id: int) -> list[Question]:
    stmt = (
        select(Question)
        .where(Question.notion_id == notion_id)
        .options(selectinload(Question.answers))
    )
    return list(db.scalars(stmt).all())