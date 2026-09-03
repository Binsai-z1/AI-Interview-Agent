import uuid

from fastapi import FastAPI, HTTPException

from app.agent.interview_agent import InterviewAgent
from app.api_models import (
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
    GetSessionResponse,
)
from app.domain.session import InterviewSession
from app.llm.gemini_client import GeminiClient
from fastapi.responses import StreamingResponse


app = FastAPI(
    title="AI Interview Agent",
    description="AI 技术面试模拟 Agent",
    version="1.0.0",
)


agent = InterviewAgent(GeminiClient())

sessions: dict[str, InterviewSession] = {}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/sessions", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest):
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        target_question_count=request.target_question_count,
    )

    sessions[session.session_id] = session

    return CreateSessionResponse(
        session_id=session.session_id,
        status=session.status.value,
        target_question_count=session.target_question_count,
    )


@app.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
)
def send_message(
    session_id: str,
    request: SendMessageRequest,
):
    session = sessions.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session 不存在",
        )

    response = agent.handle_message(
        session,
        request.message,
    )

    return SendMessageResponse(
        session_id=session.session_id,
        status=session.status.value,
        response=response,
    )

@app.post("/sessions/{session_id}/messages/stream")
def send_message_stream(
    session_id: str,
    request: SendMessageRequest,
):
    session = sessions.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session 不存在",
        )

    return StreamingResponse(
        agent.handle_message_stream(
            session,
            request.message,
        ),
        media_type="text/plain",
    )

@app.get(
    "/sessions/{session_id}",
    response_model=GetSessionResponse,
)
def get_session(session_id: str):
    session = sessions.get(session_id)

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