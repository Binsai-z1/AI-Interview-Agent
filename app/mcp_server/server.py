from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AI Interview Tools")


@mcp.tool()
def get_interview_question(
    topic: str | None = None,
    difficulty: str | None = None,
) -> dict:
    """获取一道技术面试题。"""

    questions = [
        {
            "question": "请解释一下 RAG 的基本工作流程。",
            "topic": "RAG",
            "difficulty": "easy",
        },
        {
            "question": "RAG 中的检索阶段和生成阶段分别承担什么作用？",
            "topic": "RAG",
            "difficulty": "medium",
        },
        {
            "question": "为什么 RAG 可以缓解 LLM 的知识幻觉问题？",
            "topic": "RAG",
            "difficulty": "medium",
        },
        {
            "question": "请解释一下 Prompt Engineering 的基本原理。",
            "topic": "Prompt Engineering",
            "difficulty": "easy",
        },
        {
            "question": "请解释一下 Agent 和普通 LLM Application 的主要区别。",
            "topic": "Agent",
            "difficulty": "medium",
        },
    ]

    candidates = questions

    if topic:
        candidates = [
            q for q in candidates
            if q["topic"].lower() == topic.lower()
        ]

    if difficulty:
        candidates = [
            q for q in candidates
            if q["difficulty"].lower() == difficulty.lower()
        ]

    if not candidates:
        return {
            "found": False,
            "question": None,
            "topic": topic,
            "difficulty": difficulty,
        }

    return {
        "found": True,
        **candidates[0],
    }


if __name__ == "__main__":
    mcp.run()