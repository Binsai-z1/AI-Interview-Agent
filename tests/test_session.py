from app.domain.session import InterviewSession
from app.domain.states import InterviewStatus


def test_create_session():
    session = InterviewSession(
        session_id="test_001"
    )

    assert session.session_id == "test_001"
    assert session.status == InterviewStatus.CREATED
    assert session.question_count == 0
    assert session.follow_up_count == 0
    assert session.history == []

def test_history_is_independent():
    session1 = InterviewSession(
        session_id="001"
    )

    session2 = InterviewSession(
        session_id="002"
    )

    session1.history.append(
        {
            "role": "user",
            "content": "hello"
        }
    )

    assert len(session1.history) == 1
    assert len(session2.history) == 0