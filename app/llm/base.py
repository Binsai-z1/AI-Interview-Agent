from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        ...

    def generate_stream(self, prompt: str):
        ...

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
    ) -> str:
        ...