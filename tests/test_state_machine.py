import pytest

from app.domain.events import InterviewEvent
from app.domain.state_machine import InterviewStateMachine
from app.domain.states import InterviewStatus


def test_start_interview():
    machine = InterviewStateMachine()

    next_status = machine.transition(
        InterviewStatus.CREATED,
        InterviewEvent.START_INTERVIEW,
    )

    assert next_status == InterviewStatus.ASKING


def test_question_sent():
    machine = InterviewStateMachine()

    next_status = machine.transition(
        InterviewStatus.ASKING,
        InterviewEvent.QUESTION_SENT,
    )

    assert next_status == InterviewStatus.WAITING_FOR_ANSWER


def test_answer_received():
    machine = InterviewStateMachine()

    next_status = machine.transition(
        InterviewStatus.WAITING_FOR_ANSWER,
        InterviewEvent.ANSWER_RECEIVED,
    )

    assert next_status == InterviewStatus.EVALUATING

def test_invalid_transition():
    machine = InterviewStateMachine()

    with pytest.raises(ValueError):
        machine.transition(
            InterviewStatus.CREATED,
            InterviewEvent.ANSWER_RECEIVED,
        )


def test_question_limit_completes_interview():
    machine = InterviewStateMachine()

    assert machine.transition(
        InterviewStatus.NEXT_QUESTION,
        InterviewEvent.QUESTION_LIMIT_REACHED,
    ) == InterviewStatus.COMPLETED


def test_cancel_is_allowed_from_any_active_state():
    machine = InterviewStateMachine()

    assert machine.transition(
        InterviewStatus.WAITING_FOR_ANSWER,
        InterviewEvent.CANCEL,
    ) == InterviewStatus.CANCELLED
