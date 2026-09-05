from app.domain.session import InterviewSession
from app.graph.graph import build_graph
from app.llm.base import LLMClient


class InterviewAgent:
    def __init__(self, llm: LLMClient):
        self.graph = build_graph(llm)

    def handle_message(
        self,
        session: InterviewSession,
        message: str,
    ) -> str:
        result = self.graph.invoke(
            {
                "session": session,
                "message": message,
                "response": "",
                "event": None,
                "evaluation": None,
            }
        )

        return result["response"]

    def handle_message_stream(
        self,
        session: InterviewSession,
        message: str,
    ):
        response = self.handle_message(
            session,
            message,
        )

        yield from self._stream_text(response)

    @staticmethod
    def _stream_text(
        text: str,
        chunk_size: int = 10,
    ):
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]