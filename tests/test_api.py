from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_session():
    response = client.post(
        "/sessions",
        json={
            "target_question_count": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "session_id" in data
    assert data["status"] == "created"
    assert data["target_question_count"] == 3


def test_get_session():
    create_response = client.post(
        "/sessions",
        json={
            "target_question_count": 3,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.get(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["status"] == "created"
    assert data["question_count"] == 0
    assert data["history"] == []


def test_get_nonexistent_session():
    response = client.get(
        "/sessions/nonexistent-session"
    )

    assert response.status_code == 404

def test_send_message():
    create_response = client.post(
        "/sessions",
        json={
            "target_question_count": 3,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={
            "message": "开始面试",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["status"] == "waiting_for_answer"
    assert data["response"]


def test_send_message_to_nonexistent_session():
    response = client.post(
        "/sessions/nonexistent-session/messages",
        json={
            "message": "开始面试",
        },
    )

    assert response.status_code == 404

from app.agent.interview_agent import InterviewAgent
from app.llm.fake import FakeLLMClient

def test_send_answer():
    fake_llm = FakeLLMClient(
        {
            "decision": "follow_up",
            "score": 4,
            "reason": "回答过于简略",
            "missing_points": [
                "检索过程",
                "生成过程",
            ],
        }
    )

    app_agent = InterviewAgent(fake_llm)

    from app import main

    original_agent = main.agent
    main.agent = app_agent

    try:
        create_response = client.post(
            "/sessions",
            json={
                "target_question_count": 3,
            },
        )

        session_id = create_response.json()["session_id"]

        start_response = client.post(
            f"/sessions/{session_id}/messages",
            json={
                "message": "开始面试",
            },
        )

        assert start_response.status_code == 200
        assert start_response.json()["status"] == "waiting_for_answer"

        answer_response = client.post(
            f"/sessions/{session_id}/messages",
            json={
                "message": "RAG 就是搜索资料然后回答。",
            },
        )

        assert answer_response.status_code == 200

        data = answer_response.json()

        assert data["session_id"] == session_id
        assert data["status"] == "waiting_for_answer"
        assert data["response"]

    finally:
        main.agent = original_agent

def test_create_session_with_invalid_question_count():
    response = client.post(
        "/sessions",
        json={"target_question_count": 0},
    )

    assert response.status_code == 422


def test_send_empty_message():
    create_response = client.post(
        "/sessions",
        json={"target_question_count": 3},
    )

    session_id = create_response.json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_send_message_with_missing_message():
    create_response = client.post(
        "/sessions",
        json={"target_question_count": 3},
    )

    session_id = create_response.json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={},
    )

    assert response.status_code == 422

def test_send_message_stream():
    create_response = client.post(
        "/sessions",
        json={"target_question_count": 3},
    )

    session_id = create_response.json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages/stream",
        json={"message": "开始面试"},
    )

    assert response.status_code == 200
    assert response.text
    assert "RAG" in response.text