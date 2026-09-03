import pytest

from app.llm.gemini_client import GeminiClient


@pytest.mark.integration
def test_gemini_stream():
    client = GeminiClient()

    chunks = list(
        client.generate_stream(
            "请用中文简单解释什么是 RAG。"
        )
    )

    assert chunks
    assert all(isinstance(chunk, str) for chunk in chunks)

    result = "".join(chunks)

    assert result
    print(result)