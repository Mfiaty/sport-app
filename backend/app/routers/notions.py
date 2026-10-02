from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.content import NotionDetail, NotionSummary, QuizOut
from app.services import content as content_service

router = APIRouter(prefix="/notions", tags=["notions"])


@router.get("", response_model=list[NotionSummary])
def list_notions(sport: str = "football", level: int = 1, db: Session = Depends(get_db)):
    """Liste des notions d'un sport et d'un niveau, dans l'ordre du parcours."""
    return content_service.list_notions(db, sport, level)


@router.get("/{notion_id}", response_model=NotionDetail)
def get_notion(notion_id: int, db: Session = Depends(get_db)):
    """Une notion avec les écrans de sa leçon."""
    notion = content_service.get_notion_detail(db, notion_id)
    if notion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notion introuvable")
    return notion


@router.get("/{notion_id}/quiz", response_model=QuizOut)
def get_quiz(notion_id: int, db: Session = Depends(get_db)):
    """5 questions tirées au sort, une par paire, réponses mélangées."""
    notion = content_service.get_notion_detail(db, notion_id)
    if notion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notion introuvable")
    return content_service.build_quiz(db, notion)