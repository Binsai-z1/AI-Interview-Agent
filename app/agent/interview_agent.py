from app.agent.evaluator import AnswerEvaluator
from app.agent.intent_detector import IntentDetector
from app.agent.response_generator import ResponseGenerator
from app.domain.events import InterviewEvent
from app.domain.session import InterviewSession
from app.domain.state_machine import InterviewStateMachine
from app.domain.states import InterviewStatus
from app.llm.base import LLMClient


class InterviewAgent:

    def __init__(self, llm: LLMClient):
        self.intent_detector = IntentDetector()
        self.state_machine = InterviewStateMachine()
        self.response_generator = ResponseGenerator()
        self.evaluator = AnswerEvaluator(llm)

    def handle_message(self, session: InterviewSession, message: str) -> str:
        event = self.intent_detector.detect(message)
        if event == InterviewEvent.CANCEL:
            if session.status in (InterviewStatus.CANCELLED, InterviewStatus.COMPLETED):
                return self._terminal_response(session.status)
            session.history.append({"role": "user", "content": message})
            session.status = self.state_machine.transition(session.status, event)
            response = "本次面试已取消。"
            session.history.append({"role": "assistant", "content": response})
            return response

        if session.status in (InterviewStatus.CANCELLED, InterviewStatus.COMPLETED):
            return self._terminal_response(session.status)

        if session.status == InterviewStatus.WAITING_FOR_ANSWER:
            session.current_answer = message
            session.history.append({"role": "user", "content": message})
            session.status = self.state_machine.transition(
                session.status, InterviewEvent.ANSWER_RECEIVED
            )
            evaluation = self.evaluator.evaluate_answer(message)
            session.last_evaluation = evaluation.model_dump()

            if evaluation.decision == "follow_up":
                decision = InterviewEvent.FOLLOW_UP_DECIDED
            else:
                decision = InterviewEvent.NEXT_QUESTION_DECIDED
            if decision == InterviewEvent.FOLLOW_UP_DECIDED and session.follow_up_count >= 2:
                decision = InterviewEvent.NEXT_QUESTION_DECIDED
            session.status = self.state_machine.transition(session.status, decision)

            if session.status == InterviewStatus.FOLLOW_UP:
                session.follow_up_count += 1
                response = self.response_generator.generate_follow_up()
                session.current_question = response
                session.history.append({"role": "assistant", "content": response})
                session.status = self.state_machine.transition(
                    session.status, InterviewEvent.FOLLOW_UP_SENT
                )
                return response

            if session.question_count >= session.target_question_count:
                session.status = self.state_machine.transition(
                    session.status, InterviewEvent.QUESTION_LIMIT_REACHED
                )
                response = "本次面试结束，感谢你的参与。"
                session.history.append({"role": "assistant", "content": response})
                return response

            session.question_count += 1
            response = self.response_generator.generate_next_question(session.question_count)
            session.current_question = response
            session.current_answer = None
            session.follow_up_count = 0
            session.history.append({"role": "assistant", "content": response})
            session.status = self.state_machine.transition(
                session.status, InterviewEvent.NEXT_QUESTION_READY
            )
            session.status = self.state_machine.transition(
                session.status, InterviewEvent.QUESTION_SENT
            )
            return response

        if event is None:
            return "我没有理解你的意思"
        session.status = self.state_machine.transition(session.status, event)
        if session.status == InterviewStatus.ASKING:
            response = self.response_generator.generate_first_question()
            session.current_question = response
            session.current_answer = None
            session.question_count += 1
            session.follow_up_count = 0
            session.history.append({"role": "assistant", "content": response})
            session.status = self.state_machine.transition(
                session.status, InterviewEvent.QUESTION_SENT
            )
            return response
        return "面试状态已更新。"

    @staticmethod
    def _terminal_response(status: InterviewStatus) -> str:
        if status == InterviewStatus.COMPLETED:
            return "本次面试已经结束，感谢你的参与。"
        return "本次面试已取消。"

    def handle_message_stream(
        self,
        session: InterviewSession,
        message: str,
    ):
        response = self.handle_message(session, message)

        yield from self._stream_text(response)

    def _stream_text(self, text: str, chunk_size: int = 10):
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]