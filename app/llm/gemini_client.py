import os
from typing import Any, Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()


class GeminiClient:
    def __init__(self, model: str = "gemini-3.6-flash"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY 未配置")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError("Gemini 返回了空响应")

            return response.text

        except Exception as exc:
            raise RuntimeError(
                f"Gemini 文本生成失败: {exc}"
            ) from exc

    def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_model,
                },
            )

            if not response.text:
                raise RuntimeError("Gemini 返回了空响应")

            return response_model.model_validate_json(response.text)

        except Exception as exc:
            raise RuntimeError(
                f"Gemini 结构化输出失败: {exc}"
            ) from exc

    def generate_stream(self, prompt: str):
        try:
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as exc:
            raise RuntimeError(
                f"Gemini 流式生成失败: {exc}"
            ) from exc

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        tool_functions: dict[str, Callable],
    ) -> str:
        try:
            function_declarations = [
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                )
                for tool in tools
            ]

            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        function_declarations=function_declarations
                    )
                ]
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt)
                    ],
                )
            ]

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            while response.function_calls:
                contents.append(response.candidates[0].content)

                tool_response_parts = []

                for function_call in response.function_calls:
                    function_name = function_call.name

                    if function_name not in tool_functions:
                        raise ValueError(
                            f"未知 Tool: {function_name}"
                        )

                    function = tool_functions[function_name]
                    arguments = function_call.args or {}

                    result = function(**arguments)

                    tool_response_parts.append(
                        types.Part.from_function_response(
                            name=function_name,
                            response={"result": result},
                        )
                    )

                contents.append(
                    types.Content(
                        role="user",
                        parts=tool_response_parts,
                    )
                )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

            if not response.text:
                raise RuntimeError(
                    "Gemini Tool Calling 返回了空响应"
                )

            return response.text

        except Exception as exc:
            raise RuntimeError(
                f"Gemini Tool Calling 失败: {exc}"
            ) from exc

    def generate_with_tools_stream(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        tool_functions: dict[str, Callable],
    ):
        """
        Tool Calling + 最终回答 Streaming。

        Tool Calling 阶段先正常执行。
        当 Tool 返回结果后，使用 Gemini 原生 Streaming
        生成最终的面试问题。
        """
        try:
            function_declarations = [
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                )
                for tool in tools
            ]

            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        function_declarations=function_declarations
                    )
                ]
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt)
                    ],
                )
            ]

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            while response.function_calls:
                contents.append(response.candidates[0].content)

                tool_response_parts = []

                for function_call in response.function_calls:
                    function_name = function_call.name

                    if function_name not in tool_functions:
                        raise ValueError(
                            f"未知 Tool: {function_name}"
                        )

                    function = tool_functions[function_name]
                    arguments = function_call.args or {}

                    result = function(**arguments)

                    tool_response_parts.append(
                        types.Part.from_function_response(
                            name=function_name,
                            response={"result": result},
                        )
                    )

                contents.append(
                    types.Content(
                        role="user",
                        parts=tool_response_parts,
                    )
                )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

            if not response.text:
                raise RuntimeError(
                    "Gemini Tool Calling 返回了空响应"
                )

            # Tool 已经完成。
            # 接下来用普通 Streaming 生成最终文本。
            stream_response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
            )

            for chunk in stream_response:
                if chunk.text:
                    yield chunk.text

        except Exception as exc:
            raise RuntimeError(
                f"Gemini Tool Calling Streaming 失败: {exc}"
            ) from exc