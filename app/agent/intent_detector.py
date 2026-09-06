from app.domain.events import InterviewEvent


class IntentDetector:
    def detect(self, message: str) -> InterviewEvent | None:
        message = message.strip().lower()

        # 开始面试是前端显式系统事件，不从候选人的自然语言回答中推断。
        if any(keyword in message for keyword in ("取消面试", "结束面试", "退出面试", "停止面试")):
            return InterviewEvent.CANCEL

        return None
