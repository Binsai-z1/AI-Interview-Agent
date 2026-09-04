from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.repository import InterviewSessionRepository
from app.domain.session import InterviewSession


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return SessionLocal()


def test_create_and_get_session():
    db = create_test_db()
    repository = InterviewSessionRepository(db)

    session = InterviewSession(
        session_id="test-session-001",
        target_question_count=5,
    )

    repository.create(session)

    result = repository.get_by_session_id("test-session-001")

    assert result is not None
    assert result.session_id == "test-session-001"
    assert result.status == session.status
    assert result.target_question_count == 5
    assert result.question_count == 0

    db.close()


def test_get_nonexistent_session():
    db = create_test_db()
    repository = InterviewSessionRepository(db)

    result = repository.get_by_session_id("does-not-exist")

    assert result is None

    db.close()


def test_update_session():
    db = create_test_db()
    repository = InterviewSessionRepository(db)

    session = InterviewSession(
        session_id="test-session-002",
        target_question_count=5,
    )

    repository.create(session)

    session.question_count = 2
    session.current_question = "请解释一下 RAG 的基本原理。"
    session.current_answer = "RAG 可以通过检索外部知识增强回答。"

    repository.update(session)

    result = repository.get_by_session_id("test-session-002")

    assert result is not None
    assert result.question_count == 2
    assert result.current_question == "请解释一下 RAG 的基本原理。"
    assert result.current_answer == "RAG 可以通过检索外部知识增强回答。"

    db.close()

def test_create_rolls_back_on_error():
    db = create_test_db()
    repository = InterviewSessionRepository(db)

    session = InterviewSession(
        session_id="test-session-error",
        target_question_count=5,
    )

    original_commit = db.commit

    def failing_commit():
        raise RuntimeError("模拟数据库提交失败")

    db.commit = failing_commit

    try:
        try:
            repository.create(session)
            assert False, "应该抛出 RuntimeError"
        except RuntimeError as exc:
            assert str(exc) == "模拟数据库提交失败"
    finally:
        db.commit = original_commit
        db.close()