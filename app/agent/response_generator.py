from typing import Iterator

from app.llm.base import LLMClient


class ResponseGenerator:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm

    def generate_first_question(self) -> str:
        return (
            "请你解释一下 RAG 的基本原理，"
            "以及它为什么能够减少 LLM 的幻觉问题？"
        )

    def generate_follow_up(
        self,
        question: str,
        answer: str,
        missing_points: list[str],
    ) -> str:
        if not self.llm:
            return (
                "你刚才的回答比较简略。"
                f"请继续围绕“{question}”进行解释。"
            )

        missing = (
            "、".join(missing_points)
            if missing_points
            else "关键原理和实际工作流程"
        )

        prompt = f"""
你是一名 AI 技术面试官。

当前面试问题：
{question}

候选人的回答：
{answer}

评价中发现候选人可能缺少以下内容：
{missing}

请针对“当前面试问题”设计一个自然的追问。

要求：
1. 必须围绕当前面试问题。
2. 不要突然切换到其他技术主题。
3. 不要直接重复原问题。
4. 追问应该帮助候选人补充缺失的关键知识点。
5. 只输出追问本身，不要解释你的思考过程。
"""

        response = self.llm.generate(prompt)

        if not isinstance(response, str):
            response = str(response)

        return response

    def generate_follow_up_stream(
        self,
        question: str,
        answer: str,
        missing_points: list[str],
    ) -> Iterator[str]:
        if not self.llm:
            yield self.generate_follow_up(
                question,
                answer,
                missing_points,
            )
            return

        missing = (
            "、".join(missing_points)
            if missing_points
            else "关键原理和实际工作流程"
        )

        prompt = f"""
你是一名 AI 技术面试官。

当前面试问题：
{question}

候选人的回答：
{answer}

评价中发现候选人可能缺少以下内容：
{missing}

请针对“当前面试问题”设计一个自然的追问。

要求：
1. 必须围绕当前面试问题。
2. 不要突然切换到其他技术主题。
3. 不要直接重复原问题。
4. 追问应该帮助候选人补充缺失的关键知识点。
5. 只输出追问本身，不要解释你的思考过程。
"""

        yield from self.llm.generate_stream(prompt)

    def generate_next_question(self, question_count: int) -> str:
        if question_count == 2:
            return (
                "请你解释一下 Prompt Engineering 的基本原理，"
                "以及为什么好的 Prompt 能够提升 LLM 的输出质量？"
            )

        return (
            "请你解释一下 Agent 和普通 LLM 调用之间有什么区别？"
        )