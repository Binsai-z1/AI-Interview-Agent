import pytest 
from app.agent.models import AnswerEvaluation
from app.llm.gemini_client import GeminiClient


@pytest.mark.integration
def test_gemini_structured_output():
    client = GeminiClient()

    result = client.generate_structured(
        """
        请评价下面这个 AI 面试回答：

        RAG 就是先搜索一些资料，然后让大模型根据资料回答问题。

        请按照要求的结构进行评价。
        """,
        AnswerEvaluation,
    )

    print(result)

    assert isinstance(result, AnswerEvaluation)
    assert result.decision in ("follow_up", "next_question")
    assert 1 <= result.score <= 10
    assert isinstance(result.reason, str)
    assert isinstance(result.missing_points, list)