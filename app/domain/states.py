from enum import Enum

class InterviewStatus(str, Enum):
    CREATED = "created"
    ASKING = "asking"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    EVALUATING = "evaluating"
    FOLLOW_UP = "follow_up"
    NEXT_QUESTION = "next_question"
    COMPLETED = "completed"
    CANCELLED = "cancelled"