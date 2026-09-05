from app.tools.question_tool import get_interview_question


def test_get_interview_question():
    result = get_interview_question(
        topic="RAG",
        difficulty="medium",
    )

    assert result["found"] is True
    assert result["topic"] == "RAG"
    assert result["difficulty"] == "medium"
    assert result["question"]

import pytest

from app.llm.gemini_client import GeminiClient
from app.tools.question_tool import (
    QUESTION_TOOL_DECLARATION,
    get_interview_question,
)


@pytest.mark.integration
def test_gemini_tool_calling():
    llm = GeminiClient()

    response = llm.generate_with_tools(
        prompt="""
你是一名 AI 技术面试官。

请使用题库工具获取一道 RAG 中等难度的面试题。

获取题目后，直接向候选人提出这道题。
不要解释你调用了什么工具。
""",
        tools=[QUESTION_TOOL_DECLARATION],
        tool_functions={
            "get_interview_question": get_interview_question,
        },
    )

    assert response
    print(response)