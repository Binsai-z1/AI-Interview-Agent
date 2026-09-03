from app.llm.fake import FakeLLMClient
from app.agent.evaluator import AnswerEvaluator
from app.domain.events import InterviewEvent
from app.llm.fake import FakeLLMClient


def test_fake_llm_returns_response():
    llm = FakeLLMClient("测试结果")

    result = llm.generate("测试 Prompt")

    assert result == "测试结果"

def test_evaluator_uses_llm():
    llm = FakeLLMClient(
        {
            "decision": "follow_up",
            "score": 4,
            "reason": "回答过于简略",
            "missing_points": ["生成过程", "幻觉问题"],
        }
    )
    evaluator = AnswerEvaluator(llm)

    result = evaluator.evaluate("RAG 是检索。")

    assert result == InterviewEvent.FOLLOW_UP_DECIDED