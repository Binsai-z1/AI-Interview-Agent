from pydantic import BaseModel, Field

from app.domain.states import InterviewStatus


class InterviewSession(BaseModel):
    session_id: str

    status: InterviewStatus = InterviewStatus.CREATED

    target_question_count: int = 5
    question_count: int = 0

    current_question: str | None = None
    current_answer: str | None = None

    follow_up_count: int = 0

    history: list[dict] = Field(default_factory=list)