from langgraph.graph import END, START, StateGraph

from app.graph.nodes import InterviewGraphNodes
from app.graph.state import InterviewGraphState
from app.llm.base import LLMClient


def route_after_intent(state: InterviewGraphState):
    session = state["session"]
    event = state["event"]

    if event == "cancel":
        return "cancel"

    if session.status.value in ("cancelled", "completed"):
        return "terminal"

    if event == "start_interview":
        return "start_interview"

    if session.status.value == "waiting_for_answer":
        return "receive_answer"

    return "unknown"


def route_after_evaluation(state: InterviewGraphState):
    session = state["session"]
    evaluation = state["evaluation"]

    if (
        evaluation
        and evaluation["decision"] == "follow_up"
        and session.follow_up_count < 2
    ):
        return "follow_up"

    if session.question_count >= session.target_question_count:
        return "complete_interview"

    return "next_question"


def build_graph(llm: LLMClient):
    nodes = InterviewGraphNodes(llm)

    graph = StateGraph(InterviewGraphState)

    graph.add_node(
        "detect_intent",
        nodes.detect_intent,
    )

    graph.add_node(
        "start_interview",
        nodes.start_interview,
    )

    graph.add_node(
        "receive_answer",
        nodes.receive_answer,
    )

    graph.add_node(
        "evaluate_answer",
        nodes.evaluate_answer,
    )

    graph.add_node(
        "follow_up",
        nodes.follow_up,
    )

    graph.add_node(
        "next_question",
        nodes.next_question,
    )

    graph.add_node(
        "complete_interview",
        nodes.complete_interview,
    )

    graph.add_node(
        "cancel_interview",
        nodes.cancel_interview,
    )

    graph.add_node(
        "terminal_response",
        nodes.terminal_response,
    )

    graph.add_node(
        "unknown_message",
        nodes.unknown_message,
    )

    graph.add_edge(
        START,
        "detect_intent",
    )

    graph.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "start_interview": "start_interview",
            "receive_answer": "receive_answer",
            "cancel": "cancel_interview",
            "terminal": "terminal_response",
            "unknown": "unknown_message",
        },
    )

    graph.add_edge(
        "start_interview",
        END,
    )

    graph.add_edge(
        "receive_answer",
        "evaluate_answer",
    )

    graph.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluation,
        {
            "follow_up": "follow_up",
            "next_question": "next_question",
            "complete_interview": "complete_interview",
        },
    )

    graph.add_edge(
        "follow_up",
        END,
    )

    graph.add_edge(
        "next_question",
        END,
    )

    graph.add_edge(
        "complete_interview",
        END,
    )

    graph.add_edge(
        "cancel_interview",
        END,
    )

    graph.add_edge(
        "terminal_response",
        END,
    )

    graph.add_edge(
        "unknown_message",
        END,
    )

    return graph.compile()