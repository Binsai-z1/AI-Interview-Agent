from typing import Any, Callable


class FakeLLMClient:
    """
    用于本地开发和测试的 Fake LLM。

    不调用任何真实 LLM API。
    """

    def __init__(
        self,
        response: str | dict[str, Any] | None = None,
        evaluation: dict[str, Any] | None = None,
    ):
        # 兼容现有测试：
        # FakeLLMClient("普通文本")
        # FakeLLMClient({"decision": "...", ...})
        if isinstance(response, dict) and evaluation is None:
            evaluation = response
            response = None

        self.response = response or "这是 Fake LLM 返回的回答。"

        self.evaluation = evaluation or {
            "decision": "next_question",
            "score": 8,
            "reason": "回答包含了核心概念和基本工作流程。",
            "missing_points": [],
        }

    def generate(self, prompt: str) -> str:
        return self.response

    def generate_structured(
        self,
        prompt: str,
        response_model: type,
    ):
        return response_model.model_validate(self.evaluation)

    def generate_stream(self, prompt: str):
        """
        模拟 LLM Streaming。
        """
        chunk_size = 4

        for index in range(0, len(self.response), chunk_size):
            yield self.response[index:index + chunk_size]

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_functions: dict[str, Callable],
    ) -> str:
        """
        模拟 Tool Calling。
        """
        tool = tool_functions["get_interview_question"]

        result = tool(
            excluded_questions=self._extract_excluded_questions(prompt),
        )

        if not result["found"]:
            return "题库中暂时没有符合条件的下一道题。"

        return result["question"]

    def generate_with_tools_stream(
        self,
        prompt: str,
        tools: list[dict],
        tool_functions: dict[str, Callable],
    ):
        """
        模拟 Tool Calling + Streaming。
        """
        response = self.generate_with_tools(
            prompt,
            tools,
            tool_functions,
        )

        chunk_size = 4

        for index in range(0, len(response), chunk_size):
            yield response[index:index + chunk_size]

    @staticmethod
    def _extract_excluded_questions(prompt: str) -> list[str]:
        """
        从 Agent Prompt 中提取已经问过的问题。
        """
        marker = "已经问过的问题："

        if marker not in prompt:
            return []

        section = prompt.split(marker, 1)[1]

        if "请使用" in section:
            section = section.split("请使用", 1)[0]

        section = section.strip()

        if not section or section == "[]":
            return []

        try:
            import ast

            parsed = ast.literal_eval(section)

            if isinstance(parsed, list):
                return [
                    item
                    for item in parsed
                    if isinstance(item, str)
                ]

        except (ValueError, SyntaxError):
            pass

        return []