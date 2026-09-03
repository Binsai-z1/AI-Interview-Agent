from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):
    decision: str = Field(description="follow_up 或 next_question")
    score: int = Field(description="回答质量评分，范围 1 到 10")
    reason: str = Field(description="判断原因")
    missing_points: list[str] = Field(description="回答中缺失的关键点")