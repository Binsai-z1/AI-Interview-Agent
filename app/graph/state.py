from typing import TypedDict

from app.domain.session import InterviewSession


class InterviewGraphState(TypedDict):
    session: InterviewSession
    message: str
    response: str
    event: str | None
    evaluation: dict | None