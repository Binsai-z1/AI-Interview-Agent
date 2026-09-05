class FakeLLMClient:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response

    def generate_structured(self, prompt: str, response_model):
        return response_model.model_validate(self.response)

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_functions: dict,
    ) -> str:
        tool = tool_functions["get_interview_question"]

        result = tool()

        return result["question"]