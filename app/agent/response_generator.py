from typing import Iterator

from app.llm.base import LLMClient


class ResponseGenerator:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm

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

    def generate_final_report(
        self,
        evaluations: list[dict],
        weak_evaluations: list[dict],
    ) -> str:
        if not self.llm:
            return self._fallback_final_report(evaluations, weak_evaluations)

        prompt = self._build_final_report_prompt(evaluations, weak_evaluations)
        response = self.llm.generate(prompt)
        return response if isinstance(response, str) else str(response)

    def generate_final_report_stream(
        self,
        evaluations: list[dict],
        weak_evaluations: list[dict],
    ) -> Iterator[str]:
        if not self.llm:
            yield self._fallback_final_report(evaluations, weak_evaluations)
            return

        prompt = self._build_final_report_prompt(evaluations, weak_evaluations)
        yield from self.llm.generate_stream(prompt)

    @staticmethod
    def _build_final_report_prompt(
        evaluations: list[dict],
        weak_evaluations: list[dict],
    ) -> str:
        average = (
            sum(int(item["evaluation"].get("score", 0)) for item in evaluations)
            / len(evaluations)
            if evaluations
            else 0
        )

        weak_text = []
        for index, item in enumerate(weak_evaluations, 1):
            evaluation = item["evaluation"]
            weak_text.append(
                f"薄弱题目 {index}：\n"
                f"问题：{item.get('question', '')}\n"
                f"候选人回答：{item.get('answer', '')}\n"
                f"得分：{evaluation.get('score', '')}/10\n"
                f"评价：{evaluation.get('reason', '')}\n"
                f"缺失知识点：{'、'.join(evaluation.get('missing_points', []))}"
            )

        weak_section = "\n\n".join(weak_text) if weak_text else "本次没有明显薄弱题目。"

        return f"""
你是一名资深 AI 技术面试官，请根据本次面试的逐题评估结果生成最终面试报告。

本次共完成 {len(evaluations)} 道题，平均得分约为 {average:.1f}/10。

重点薄弱题目：
{weak_section}

完整评估记录：
{evaluations}

请直接输出中文面试总结，不要解释你的生成过程。
报告必须包含以下部分：
1. 整体评价：概括候选人的技术基础、回答质量和面试表现，并结合平均分给出总体判断。
2. 表现较好的方面：总结候选人已经掌握较好的能力。
3. 重点改进题目：针对上面的薄弱题目逐题输出：原题、候选人的主要问题、参考答案、改进建议。参考答案要能真正回答原题，具有技术细节，不能只写一句话。
4. 后续学习建议：给出 3 到 5 条最值得优先加强的方向。

如果没有薄弱题目，也要说明本次整体表现较好，并给出进一步提升建议。
"""

    @staticmethod
    def _fallback_final_report(
        evaluations: list[dict],
        weak_evaluations: list[dict],
    ) -> str:
        if not evaluations:
            return "## 整体评价\n本次面试暂无可用的逐题评估结果。"

        average = sum(
            int(item["evaluation"].get("score", 0)) for item in evaluations
        ) / len(evaluations)
        lines = [
            "## 整体评价",
            f"本次共完成 {len(evaluations)} 道题，平均得分 {average:.1f}/10。",
        ]

        if weak_evaluations:
            lines.append("\n## 重点改进题目")
            for item in weak_evaluations:
                evaluation = item["evaluation"]
                lines.extend([
                    f"\n### {item.get('question', '')}",
                    f"得分：{evaluation.get('score', '')}/10",
                    f"问题分析：{evaluation.get('reason', '')}",
                    f"缺失知识点：{'、'.join(evaluation.get('missing_points', []))}",
                    "参考答案：请围绕原题补充完整的定义、核心流程和工程实践。",
                    "改进建议：回答时先给出核心结论，再按照原理、流程和实际场景展开。",
                ])
        else:
            lines.append("\n本次没有明显薄弱题目，整体表现较好。")

        return "\n".join(lines)
