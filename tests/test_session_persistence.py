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

    return engine, SessionLocal


def test_session_can_be_restored():
    engine, SessionLocal = create_test_db()

    # 第一次运行：创建并保存 Session
    db = SessionLocal()
    repository = InterviewSessionRepository(db)

    session = InterviewSession(
        session_id="persistent-session-001",
        target_question_count=5,
    )

    session.question_count = 1
    session.current_question = "请解释一下 RAG 的基本原理。"
    session.current_answer = "RAG 通过检索外部知识增强模型回答。"
    session.history = [
        {
            "role": "assistant",
            "content": "请解释一下 RAG 的基本原理。",
        },
        {
            "role": "user",
            "content": "RAG 通过检索外部知识增强模型回答。",
        },
    ]

    repository.create(session)
    db.close()

    # 模拟重新启动：创建新的数据库 Session
    db = SessionLocal()
    repository = InterviewSessionRepository(db)

    restored_session = repository.get_by_session_id(
        "persistent-session-001"
    )

    assert restored_session is not None
    assert restored_session.session_id == "persistent-session-001"
    assert restored_session.question_count == 1
    assert restored_session.current_question == (
        "请解释一下 RAG 的基本原理。"
    )
    assert restored_session.current_answer == (
        "RAG 通过检索外部知识增强模型回答。"
    )
    assert len(restored_session.history) == 2

    db.close()