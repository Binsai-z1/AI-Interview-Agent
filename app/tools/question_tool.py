from dataclasses import dataclass


@dataclass
class InterviewQuestion:
    question: str
    topic: str
    difficulty: str


class QuestionBank:
    def __init__(self):
        self.questions = [
            InterviewQuestion(
                question="请解释一下 RAG 的基本工作流程。",
                topic="RAG",
                difficulty="easy",
            ),
            InterviewQuestion(
                question="RAG 中的检索阶段和生成阶段分别承担什么作用？",
                topic="RAG",
                difficulty="medium",
            ),
            InterviewQuestion(
                question="为什么 RAG 可以缓解 LLM 的知识幻觉问题？",
                topic="RAG",
                difficulty="medium",
            ),
            InterviewQuestion(
                question="请解释一下 Prompt Engineering 的基本原理。",
                topic="Prompt Engineering",
                difficulty="easy",
            ),
            InterviewQuestion(
                question="如何设计一个能够稳定输出结构化 JSON 的 Prompt？",
                topic="Prompt Engineering",
                difficulty="medium",
            ),
            InterviewQuestion(
                question="请解释一下 Agent 和普通 LLM Application 的主要区别。",
                topic="Agent",
                difficulty="medium",
            ),
            InterviewQuestion(
                question="LangGraph 为什么适合构建有状态的 Agent？",
                topic="Agent",
                difficulty="hard",
            ),
        ]

    def get_question(
        self,
        topic: str | None = None,
        difficulty: str | None = None,
    ) -> InterviewQuestion | None:

        candidates = self.questions

        if topic:
            candidates = [
                question
                for question in candidates
                if question.topic.lower() == topic.lower()
            ]

        if difficulty:
            candidates = [
                question
                for question in candidates
                if question.difficulty.lower() == difficulty.lower()
            ]

        if not candidates:
            return None

        return candidates[0]


question_bank = QuestionBank()


def get_interview_question(
    topic: str | None = None,
    difficulty: str | None = None,
) -> dict:

    question = question_bank.get_question(
        topic=topic,
        difficulty=difficulty,
    )

    if question is None:
        return {
            "found": False,
            "question": None,
            "topic": topic,
            "difficulty": difficulty,
        }

    return {
        "found": True,
        "question": question.question,
        "topic": question.topic,
        "difficulty": question.difficulty,
    }


QUESTION_TOOL_DECLARATION = {
    "name": "get_interview_question",
    "description": (
        "从面试题库中获取一道适合当前面试的技术面试题。"
        "可以根据技术主题和难度进行筛选。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": (
                    "技术主题，例如 RAG、Prompt Engineering、Agent"
                ),
            },
            "difficulty": {
                "type": "string",
                "enum": [
                    "easy",
                    "medium",
                    "hard",
                ],
                "description": "题目难度",
            },
        },
    },
}