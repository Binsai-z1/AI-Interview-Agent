from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    target_question_count: int = Field(default=5, ge=1)


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    target_question_count: int

class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1)


class SendMessageResponse(BaseModel):
    session_id: str
    status: str
    response: str

class GetSessionResponse(BaseModel):
    session_id: str
    status: str
    target_question_count: int
    question_count: int
    current_question: str | None
    current_answer: str | None
    follow_up_count: int
    history: list[dict]
    last_evaluation: dict | None