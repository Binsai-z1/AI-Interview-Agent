from app.agent.evaluator import AnswerEvaluator
from app.agent.intent_detector import IntentDetector
from app.agent.response_generator import ResponseGenerator
from app.domain.events import InterviewEvent
from app.domain.state_machine import InterviewStateMachine
from app.domain.states import InterviewStatus
from app.graph.state import InterviewGraphState
from app.llm.base import LLMClient
from app.tools.tools import build_tool_registry


class InterviewGraphNodes:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.intent_detector = IntentDetector()
        self.response_generator = ResponseGenerator()
        self.state_machine = InterviewStateMachine()
        self.evaluator = AnswerEvaluator(llm)
        self.tool_registry = build_tool_registry()

    def detect_intent(self, state: InterviewGraphState):
        event = self.intent_detector.detect(state["message"])

        return {
            "event": event.value if event else None,
        }

    def start_interview(self, state: InterviewGraphState):
        session = state["session"]

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.START_INTERVIEW,
        )

        response = self.response_generator.generate_first_question()

        session.current_question = response
        session.current_answer = None
        session.question_count += 1
        session.follow_up_count = 0

        session.history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.QUESTION_SENT,
        )

        return {
            "session": session,
            "response": response,
        }

    def receive_answer(self, state: InterviewGraphState):
        session = state["session"]

        session.current_answer = state["message"]

        session.history.append(
            {
                "role": "user",
                "content": state["message"],
            }
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.ANSWER_RECEIVED,
        )

        return {
            "session": session,
        }

    def evaluate_answer(self, state: InterviewGraphState):
        session = state["session"]

        evaluation = self.evaluator.evaluate_answer(
            state["message"]
        )

        evaluation_data = evaluation.model_dump()
        session.last_evaluation = evaluation_data

        return {
            "session": session,
            "evaluation": evaluation_data,
        }

    def follow_up(self, state: InterviewGraphState):
        session = state["session"]

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.FOLLOW_UP_DECIDED,
        )

        response = self.response_generator.generate_follow_up()

        session.current_question = response
        session.follow_up_count += 1

        session.history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.FOLLOW_UP_SENT,
        )

        return {
            "session": session,
            "response": response,
        }

    def next_question(self, state: InterviewGraphState):
        session = state["session"]

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.NEXT_QUESTION_DECIDED,
        )

        prompt = f"""
你是一名 AI 技术面试官。

请从题库中选择下一道适合 AI 应用开发岗位的技术面试题。

这是第 {session.question_count + 1} 道题。

候选人刚才的回答：
{session.current_answer or "无"}

请使用 get_interview_question 工具获取下一道题。

优先选择与 LLM、Prompt Engineering、RAG、Agent、
AI 应用工程相关的题目。

获取到题目后，直接输出面试问题。
不要解释工具调用过程。
"""

        response = self.llm.generate_with_tools(
            prompt=prompt,
            tools=self.tool_registry.get_declarations(),
            tool_functions=self.tool_registry.get_functions(),
        )

        session.question_count += 1
        session.current_question = response
        session.current_answer = None
        session.follow_up_count = 0

        session.history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.NEXT_QUESTION_READY,
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.QUESTION_SENT,
        )

        return {
            "session": session,
            "response": response,
        }

    def complete_interview(self, state: InterviewGraphState):
        session = state["session"]

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.NEXT_QUESTION_DECIDED,
        )

        session.status = self.state_machine.transition(
            session.status,
            InterviewEvent.QUESTION_LIMIT_REACHED,
        )

        response = "本次面试结束，感谢你的参与。"

        session.history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        return {
            "session": session,
            "response": response,
        }

    def cancel_interview(self, state: InterviewGraphState):
        session = state["session"]

        if session.status not in (
            InterviewStatus.CANCELLED,
            InterviewStatus.COMPLETED,
        ):
            session.status = self.state_machine.transition(
                session.status,
                InterviewEvent.CANCEL,
            )

            response = "本次面试已取消。"

            session.history.append(
                {
                    "role": "user",
                    "content": state["message"],
                }
            )

            session.history.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )
        else:
            response = self._terminal_response(session.status)

        return {
            "session": session,
            "response": response,
        }

    def terminal_response(self, state: InterviewGraphState):
        session = state["session"]

        response = self._terminal_response(
            session.status
        )

        return {
            "response": response,
        }

    def unknown_message(self, state: InterviewGraphState):
        return {
            "response": "我没有理解你的意思"
        }

    @staticmethod
    def _terminal_response(
        status: InterviewStatus,
    ) -> str:
        if status == InterviewStatus.COMPLETED:
            return "本次面试已经结束，感谢你的参与。"

        return "本次面试已取消。"