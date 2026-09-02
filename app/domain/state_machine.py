from app.domain.states import InterviewStatus
from app.domain.events import InterviewEvent


class InterviewStateMachine:

    def transition(
        self,
        current_status: InterviewStatus,
        event: InterviewEvent,
    ) -> InterviewStatus:

        if (
            current_status == InterviewStatus.CREATED
            and event == InterviewEvent.START_INTERVIEW
        ):
            return InterviewStatus.ASKING

        if (
            current_status == InterviewStatus.ASKING
            and event == InterviewEvent.QUESTION_SENT
        ):
            return InterviewStatus.WAITING_FOR_ANSWER

        if (
            current_status == InterviewStatus.WAITING_FOR_ANSWER
            and event == InterviewEvent.ANSWER_RECEIVED
        ):
            return InterviewStatus.EVALUATING

        if (
            current_status == InterviewStatus.EVALUATING
            and event == InterviewEvent.FOLLOW_UP_DECIDED
        ):
            return InterviewStatus.FOLLOW_UP

        if (
            current_status == InterviewStatus.EVALUATING
            and event == InterviewEvent.NEXT_QUESTION_DECIDED
        ):
            return InterviewStatus.NEXT_QUESTION

        if (
            current_status == InterviewStatus.FOLLOW_UP
            and event == InterviewEvent.FOLLOW_UP_SENT
        ):
            return InterviewStatus.WAITING_FOR_ANSWER

        if (
            current_status == InterviewStatus.NEXT_QUESTION
            and event == InterviewEvent.NEXT_QUESTION_READY
        ):
            return InterviewStatus.ASKING

        if event == InterviewEvent.CANCEL:
            return InterviewStatus.CANCELLED

        raise ValueError(
            f"Invalid transition: {current_status} + {event}"
        )