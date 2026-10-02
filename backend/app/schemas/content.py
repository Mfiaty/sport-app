from pydantic import BaseModel, ConfigDict


class NotionSummary(BaseModel):
    """Une notion dans la liste du parcours."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    level: int
    position: int
    title: str


class LessonScreenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    title: str
    body: str
    image_url: str | None
    is_fun_fact: bool


class NotionDetail(NotionSummary):
    """Une notion avec tous les écrans de sa leçon."""

    screens: list[LessonScreenOut]


class QuizAnswerOut(BaseModel):
    # Volontairement sans is_correct ni why_wrong :
    # le navigateur ne doit jamais recevoir les bonnes réponses.
    id: int
    text: str


class QuizQuestionOut(BaseModel):
    id: int
    pair_number: int
    difficulty: int
    statement: str
    image_url: str | None
    answers: list[QuizAnswerOut]


class QuizOut(BaseModel):
    notion_id: int
    notion_title: str
    questions: list[QuizQuestionOut]