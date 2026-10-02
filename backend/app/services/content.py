import random
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Notion, Question
from app.repositories import content as content_repo
from app.schemas.content import QuizAnswerOut, QuizOut, QuizQuestionOut

# Générateur aléatoire basé sur le système : le tirage n'est pas prévisible
_rng = random.SystemRandom()


def list_notions(db: Session, sport_slug: str, level: int) -> list[Notion]:
    return content_repo.list_notions(db, sport_slug, level)


def get_notion_detail(db: Session, notion_id: int) -> Notion | None:
    return content_repo.get_notion_with_screens(db, notion_id)


def draw_one_per_pair(questions: list[Question]) -> list[Question]:
    """Tire au sort une question par paire, dans l'ordre des paires."""
    pairs: dict[int, list[Question]] = defaultdict(list)
    for question in questions:
        pairs[question.pair_number].append(question)
    return [_rng.choice(pairs[number]) for number in sorted(pairs)]


def build_quiz(db: Session, notion: Notion) -> QuizOut:
    questions = content_repo.get_questions_with_answers(db, notion.id)
    drawn = draw_one_per_pair(questions)

    quiz_questions = []
    for question in drawn:
        answers = list(question.answers)
        _rng.shuffle(answers)  # l'ordre des réponses change à chaque passage
        quiz_questions.append(
            QuizQuestionOut(
                id=question.id,
                pair_number=question.pair_number,
                difficulty=question.difficulty,
                statement=question.statement,
                image_url=question.image_url,
                answers=[QuizAnswerOut(id=a.id, text=a.text) for a in answers],
            )
        )

    return QuizOut(notion_id=notion.id, notion_title=notion.title, questions=quiz_questions)