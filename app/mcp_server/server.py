import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Support both ``python -m app.mcp_server.server`` and the existing client
# command: ``python app/mcp_server/server.py``.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.question_tool import get_interview_question as _get_interview_question


mcp = FastMCP("AI Interview Tools")


@mcp.tool()
def get_interview_question(
    topic: str | None = None,
    difficulty: str | None = None,
    excluded_questions: list[str] | None = None,
) -> dict:
    """获取一道技术面试题，并可排除已经问过的问题。"""
    return _get_interview_question(
        topic=topic,
        difficulty=difficulty,
        excluded_questions=excluded_questions,
    )


if __name__ == "__main__":
    mcp.run()
