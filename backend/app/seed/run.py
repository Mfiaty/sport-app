"""Insère le contenu pédagogique (fichiers JSON du dossier data/) dans la base.

Lancement, depuis le dossier backend avec le .venv actif :
    python -m app.seed.run

Le script peut être relancé autant de fois que nécessaire : il met à jour
les notions existantes au lieu de créer des doublons.
"""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Answer, LessonScreen, Notion, Question, Sport

DATA_DIR = Path(__file__).parent / "data"
EXPECTED_SLOTS = {(pair, variant) for pair in range(1, 6) for variant in ("a", "b")}


def validate(data: dict, source: str) -> None:
    """Refuse un fichier incomplet ou incohérent avant de toucher à la base."""
    for notion in data["notions"]:
        title = notion["title"]

        slots = {(q["pair"], q["variant"]) for q in notion["questions"]}
        if slots != EXPECTED_SLOTS:
            missing = sorted(EXPECTED_SLOTS - slots)
            raise ValueError(f"{source} — « {title} » : paires incomplètes, manquent {missing}")

        for q in notion["questions"]:
            correct = sum(1 for a in q["answers"] if a["correct"])
            if correct != 1:
                raise ValueError(
                    f"{source} — « {title} », question {q['pair']}{q['variant']} : "
                    f"{correct} bonne(s) réponse(s) au lieu d'une seule"
                )


def get_or_create_sport(db: Session, slug: str, name: str) -> Sport:
    sport = db.scalar(select(Sport).where(Sport.slug == slug))
    if sport is None:
        sport = Sport(slug=slug, name=name)
        db.add(sport)
        db.flush()
    else:
        sport.name = name
    return sport


def seed_notion(db: Session, sport: Sport, data: dict) -> None:
    notion = db.scalar(
        select(Notion).where(
            Notion.sport_id == sport.id,
            Notion.level == data["level"],
            Notion.position == data["position"],
        )
    )
    if notion is None:
        notion = Notion(sport_id=sport.id, level=data["level"], position=data["position"])
        db.add(notion)

    notion.title = data["title"]

    # On vide l'ancien contenu de la notion, puis on le recrée.
    # Le flush applique les suppressions avant les insertions.
    notion.screens.clear()
    notion.questions.clear()
    db.flush()

    for s in data["screens"]:
        notion.screens.append(
            LessonScreen(
                position=s["position"],
                title=s["title"],
                body=s["body"],
                image_url=s.get("image_url"),
                is_fun_fact=s.get("is_fun_fact", False),
            )
        )

    for q in data["questions"]:
        question = Question(
            pair_number=q["pair"],
            variant=q["variant"],
            difficulty=q["difficulty"],
            statement=q["statement"],
            image_url=q.get("image_url"),
            explanation=q["explanation"],
        )
        for a in q["answers"]:
            question.answers.append(
                Answer(
                    text=a["text"],
                    is_correct=a["correct"],
                    why_wrong=a.get("why_wrong"),
                )
            )
        notion.questions.append(question)


def seed_file(db: Session, path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data, path.name)

    sport = get_or_create_sport(db, data["sport"]["slug"], data["sport"]["name"])
    for notion_data in data["notions"]:
        seed_notion(db, sport, notion_data)

    nb_questions = sum(len(n["questions"]) for n in data["notions"])
    print(f"✔ {path.name} : {len(data['notions'])} notions, {nb_questions} questions")


def main() -> None:
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        print(f"Aucun fichier JSON trouvé dans {DATA_DIR}")
        return

    with SessionLocal() as db:
        try:
            for path in files:
                seed_file(db, path)
            db.commit()
            print("Contenu enregistré dans la base.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()