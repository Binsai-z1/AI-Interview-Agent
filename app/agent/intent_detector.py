from app.domain.events import InterviewEvent


class IntentDetector:

    def detect(self, message: str) -> InterviewEvent | None:

        message = message.lower()

        if (
            "开始" in message
            or "准备好了" in message
            or "可以了" in message
        ):
            return InterviewEvent.START_INTERVIEW

        if any(keyword in message for keyword in ("取消", "结束", "退出", "停止")):
            return InterviewEvent.CANCEL

        return None
