from typing import Any, Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._declarations: list[dict[str, Any]] = []

    def register(
        self,
        name: str,
        function: Callable,
        declaration: dict[str, Any],
    ):
        self._tools[name] = function
        self._declarations.append(declaration)

    def get_functions(self) -> dict[str, Callable]:
        return self._tools.copy()

    def get_declarations(self) -> list[dict[str, Any]]:
        return self._declarations.copy()