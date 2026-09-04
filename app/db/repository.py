from sqlalchemy.orm import Session

from app.db.models import InterviewSessionModel
from app.domain.session import InterviewSession


class InterviewSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: InterviewSession) -> InterviewSession:
        model = InterviewSessionModel(
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

        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
        except Exception:
            self.db.rollback()
            raise

        return session

    def get_by_session_id(
        self,
        session_id: str,
    ) -> InterviewSession | None:
        model = (
            self.db.query(InterviewSessionModel)
            .filter(
                InterviewSessionModel.session_id == session_id
            )
            .first()
        )

        if model is None:
            return None

        return InterviewSession(
            session_id=model.session_id,
            status=model.status,
            target_question_count=model.target_question_count,
            question_count=model.question_count,
            current_question=model.current_question,
            current_answer=model.current_answer,
            follow_up_count=model.follow_up_count,
            history=model.history or [],
            last_evaluation=model.last_evaluation,
        )

    def update(self, session: InterviewSession) -> InterviewSession:
        model = (
            self.db.query(InterviewSessionModel)
            .filter(
                InterviewSessionModel.session_id == session.session_id
            )
            .first()
        )

        if model is None:
            raise ValueError(
                f"Session 不存在: {session.session_id}"
            )

        model.status = session.status.value
        model.target_question_count = session.target_question_count
        model.question_count = session.question_count
        model.current_question = session.current_question
        model.current_answer = session.current_answer
        model.follow_up_count = session.follow_up_count
        model.history = session.history
        model.last_evaluation = session.last_evaluation

        try:
            self.db.commit()
            self.db.refresh(model)
        except Exception:
            self.db.rollback()
            raise

        return session