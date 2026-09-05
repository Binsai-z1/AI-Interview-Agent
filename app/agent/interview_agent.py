import queue
import threading

from app.domain.session import InterviewSession
from app.graph.graph import build_graph
from app.llm.base import LLMClient


class InterviewAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm
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
                "stream_callback": None,
            }
        )

        return result["response"]

    def handle_message_stream(
        self,
        session: InterviewSession,
        message: str,
    ):
        """
        真正的 Streaming。

        Graph 在后台线程执行。
        Gemini 产生的每个 chunk
        通过 callback 放入 queue。
        当前生成器负责不断向 HTTP 层 yield。
        """

        chunk_queue: queue.Queue = queue.Queue()
        sentinel = object()

        def emit(chunk: str):
            chunk_queue.put(chunk)

        def run_graph():
            try:
                self.graph.invoke(
                    {
                        "session": session,
                        "message": message,
                        "response": "",
                        "event": None,
                        "evaluation": None,
                        "stream_callback": emit,
                    }
                )
            except Exception as exc:
                chunk_queue.put(exc)
            finally:
                chunk_queue.put(sentinel)

        thread = threading.Thread(
            target=run_graph,
            daemon=True,
        )

        thread.start()

        while True:
            item = chunk_queue.get()

            if item is sentinel:
                break

            if isinstance(item, Exception):
                raise item

            yield item