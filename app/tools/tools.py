from app.tools.question_tool import (
    QUESTION_TOOL_DECLARATION,
    get_interview_question,
)
from app.tools.registry import ToolRegistry


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        name="get_interview_question",
        function=get_interview_question,
        declaration=QUESTION_TOOL_DECLARATION,
    )

    return registry