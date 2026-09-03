from app.agent.models import AnswerEvaluation
from app.llm.fake import FakeLLMClient


def test_structured_output():
    llm = FakeLLMClient(
        {
            "decision": "follow_up",
            "score": 4,
            "reason": "回答过于简略",
            "missing_points": ["生成过程", "幻觉问题"],
        }
    )

    result = llm.generate_structured(
        "请评价这个回答",
        AnswerEvaluation,
    )

    assert isinstance(result, AnswerEvaluation)
    assert result.decision == "follow_up"
    assert result.score == 4
    assert result.missing_points == ["生成过程", "幻觉问题"]

from app.agent.evaluator import AnswerEvaluator


def test_evaluator_returns_structured_evaluation():
    llm = FakeLLMClient(
        {
            "decision": "follow_up",
            "score": 4,
            "reason": "回答过于简略",
            "missing_points": ["生成过程", "幻觉问题"],
        }
    )

    evaluator = AnswerEvaluator(llm)

    result = evaluator.evaluate_answer("RAG 就是搜索资料。")

    assert isinstance(result, AnswerEvaluation)
    assert result.decision == "follow_up"
    assert result.score == 4
    assert result.reason == "回答过于简略"
    assert result.missing_points == ["生成过程", "幻觉问题"]