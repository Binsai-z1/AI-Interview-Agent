from typing import Callable, TypedDict

from app.domain.session import InterviewSession


class InterviewGraphState(TypedDict):
    session: InterviewSession
    message: str
    response: str
    event: str | None
    evaluation: dict | None
    stream_callback: Callable[[str], None] | None