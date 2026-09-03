class ResponseGenerator:

    def generate_first_question(self) -> str:
        return (
            "请你解释一下 RAG 的基本原理，"
            "以及它为什么能够减少 LLM 的幻觉问题？"
        )

    def generate_follow_up(self) -> str:
        return (
            "你刚才的回答比较简略。"
            "能进一步解释一下 RAG 中的检索和生成分别承担什么作用吗？"
        )

    def generate_next_question(self, question_count: int) -> str:
        if question_count == 2:
            return (
                "请你解释一下 Prompt Engineering 的基本原理，"
                "以及为什么好的 Prompt 能够提升 LLM 的输出质量？"
            )

        return (
            "请你解释一下 Agent 和普通 LLM 调用之间有什么区别？"
        )