import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agent.interview_agent import InterviewAgent
from app.api_models import (
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.db.database import get_db
from app.db.repository import InterviewSessionRepository
from app.domain.session import InterviewSession
from app.llm.gemini_client import GeminiClient


app = FastAPI(
    title="AI Interview Agent",
    description="AI 技术面试模拟 Agent",
    version="1.0.0",
)

agent = InterviewAgent(GeminiClient())


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/sessions", response_model=CreateSessionResponse)
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
):
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        target_question_count=request.target_question_count,
    )

    repository = InterviewSessionRepository(db)
    repository.create(session)

    return CreateSessionResponse(
        session_id=session.session_id,
        status=session.status.value,
        target_question_count=session.target_question_count,
    )


@app.get(
    "/sessions/{session_id}",
    response_model=GetSessionResponse,
)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    repository = InterviewSessionRepository(db)
    session = repository.get_by_session_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session 不存在",
        )

    return GetSessionResponse(
        session_id=session.session_id,
        status=session.status.value,
        target_question_count=session.target_question_count,
        question_count=session.question_count,
        current_question=session.current_question,
        current_answer=session.current_answer,
        follow_up_count=session.follow_up_count,
        history=session.history,
        last_evaluation=session.last_evaluation,
    )


@app.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
)
def send_message(
    session_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
):
    repository = InterviewSessionRepository(db)

    session = repository.get_by_session_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session 不存在",
        )

    response = agent.handle_message(
        session,
        request.message,
    )

    repository.update(session)

    return SendMessageResponse(
        session_id=session.session_id,
        status=session.status.value,
        response=response,
    )


@app.post("/sessions/{session_id}/messages/stream")
def send_message_stream(
    session_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
):
    repository = InterviewSessionRepository(db)

    session = repository.get_by_session_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session 不存在",
        )

    response = agent.handle_message(
        session,
        request.message,
    )

    repository.update(session)

    return StreamingResponse(
        agent._stream_text(response),
        media_type="text/plain",
    )