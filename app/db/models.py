from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class InterviewSessionModel(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    target_question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    current_question: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    current_answer: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    follow_up_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    history: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    last_evaluation: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )