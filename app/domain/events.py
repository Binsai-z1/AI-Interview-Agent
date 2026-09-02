from enum import Enum


class InterviewEvent(str, Enum):
    START_INTERVIEW = "start_interview"
    QUESTION_SENT = "question_sent"
    ANSWER_RECEIVED = "answer_received"
    FOLLOW_UP_DECIDED = "follow_up_decided"
    NEXT_QUESTION_DECIDED = "next_question_decided"
    FOLLOW_UP_SENT = "follow_up_sent"
    NEXT_QUESTION_READY = "next_question_ready"
    QUESTION_LIMIT_REACHED = "question_limit_reached"
    CANCEL = "cancel"