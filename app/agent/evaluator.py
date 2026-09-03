from app.agent.models import AnswerEvaluation
from app.domain.events import InterviewEvent
from app.llm.base import LLMClient


class AnswerEvaluator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def evaluate(self, answer: str) -> InterviewEvent:
        evaluation = self.evaluate_answer(answer)

        if evaluation.decision == "follow_up":
            return InterviewEvent.FOLLOW_UP_DECIDED

        return InterviewEvent.NEXT_QUESTION_DECIDED

    def evaluate_answer(self, answer: str) -> AnswerEvaluation:
        prompt = f"""
你是一名 AI 技术面试官。

请评价候选人的回答。

候选人回答：
{answer}

请根据回答质量进行评价：
1. decision：如果回答过于简略或缺少关键内容，返回 follow_up；
   如果回答已经足够完整，返回 next_question。
2. score：给出 1 到 10 的评分。
3. reason：说明你的判断原因。
4. missing_points：列出候选人回答中缺失的关键知识点。

请严格按照要求的结构返回。
"""

        return self.llm.generate_structured(
            prompt,
            AnswerEvaluation,
        )