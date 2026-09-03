import pytest
from app.llm.gemini_client import GeminiClient

@pytest.mark.integration
def test_real_gemini_call():
    client = GeminiClient()

    result = client.generate(
        "请只回答：RAG 是什么？"
    )

    print(result)

    assert result