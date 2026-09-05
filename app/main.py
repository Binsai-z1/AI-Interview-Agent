import uuid
import json

from fastapi.responses import StreamingResponse
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.agent.interview_agent import InterviewAgent
from app.api_models import (
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.db.database import Base, engine, get_db
from app.db import models
from app.db.repository import InterviewSessionRepository
from app.domain.session import InterviewSession
from app.llm.gemini_client import GeminiClient

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AI Interview Agent",
    description="AI 技术面试模拟 Agent",
    version="1.0.0",
)

@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        raise HTTPException(status_code=404, detail="Session 不存在")

    def sse_event(event: str, data: dict) -> str:
        return (
            f"event: {event}\n"
            f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        )

    def generate():
        try:
            for chunk in agent.handle_message_stream(
                session,
                request.message,
            ):
                yield sse_event(
                    "token",
                    {"content": chunk},
                )

            repository.update(session)

            yield sse_event(
                "done",
                {
                    "status": session.status.value,
                    "question_count": session.question_count,
                    "follow_up_count": session.follow_up_count,
                },
            )

        except HTTPException as exc:
            db.rollback()

            yield sse_event(
                "error",
                {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                },
            )

        except Exception as exc:
            db.rollback()

            yield sse_event(
                "error",
                {
                    "code": "INTERNAL_ERROR",
                    "message": str(exc),
                },
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )