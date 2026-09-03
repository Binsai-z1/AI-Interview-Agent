import os

from google import genai
from pydantic import BaseModel


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