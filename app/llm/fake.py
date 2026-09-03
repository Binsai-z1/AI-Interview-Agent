class FakeLLMClient:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response

    def generate_structured(self, prompt: str, response_model):
        return response_model.model_validate(self.response)