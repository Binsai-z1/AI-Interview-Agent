import pytest

from app.agent.interview_agent import InterviewAgent
from app.domain.session import InterviewSession
from app.domain.states import InterviewStatus
from app.llm.fake import FakeLLMClient


@pytest.fixture
def make_agent():
    def _make(response="next_question"):
        evaluation = {
            "decision": response,
            "score": 8,
            "reason": "回答基本完整",
            "missing_points": [],
        }

        return InterviewAgent(FakeLLMClient(evaluation))

    return _make


def test_start_interview(make_agent):
    agent = make_agent()
    session = InterviewSession(session_id="test_001")

    response = agent.handle_message(
        session,
        "我准备好了",
    )

    assert session.status == InterviewStatus.WAITING_FOR_ANSWER
    assert session.question_count == 1
    assert session.current_question is not None
    assert response == session.current_question
    assert session.history == [
        {"role": "assistant", "content": response}
    ]


def test_receive_answer(make_agent):
    agent = make_agent()
    session = InterviewSession(session_id="test_001")

    first_question = agent.handle_message(
        session,
        "我准备好了",
    )

    response = agent.handle_message(
        session,
        "RAG 是先从知识库检索相关内容，再把这些内容交给 LLM 生成答案。",
    )

    assert session.status == InterviewStatus.WAITING_FOR_ANSWER
    assert session.question_count == 2
    assert session.current_answer is None
    assert session.current_question is not None
    assert session.current_question != first_question
    assert response == session.current_question

    assert session.history == [
        {"role": "assistant", "content": first_question},
        {
            "role": "user",
            "content": "RAG 是先从知识库检索相关内容，再把这些内容交给 LLM 生成答案。",
        },
        {"role": "assistant", "content": response},
    ]


def test_weak_answer_triggers_follow_up(make_agent):
    agent = make_agent("follow_up")
    session = InterviewSession(session_id="test_001")

    agent.handle_message(
        session,
        "我准备好了",
    )

    response = agent.handle_message(
        session,
        "RAG 是检索。",
    )

    assert session.status == InterviewStatus.WAITING_FOR_ANSWER
    assert session.follow_up_count == 1
    assert session.current_question == response


def test_follow_up_limit(make_agent):
    agent = make_agent("follow_up")
    session = InterviewSession(session_id="test_003")

    agent.handle_message(
        session,
        "我准备好了",
    )

    agent.handle_message(
        session,
        "RAG 是检索。",
    )

    assert session.follow_up_count == 1
    assert session.status == InterviewStatus.WAITING_FOR_ANSWER

    agent.handle_message(
        session,
        "还是检索。",
    )

    assert session.follow_up_count == 2
    assert session.status == InterviewStatus.WAITING_FOR_ANSWER

    # 第三次追问达到上限，因此进入下一题
    response = agent.handle_message(
        session,
        "不知道。",
    )

    assert session.follow_up_count == 0
    assert session.status == InterviewStatus.WAITING_FOR_ANSWER
    assert session.question_count == 2
    assert response == session.current_question


def test_interview_completes_at_question_limit(make_agent):
    agent = make_agent()
    session = InterviewSession(
        session_id="test_004",
        target_question_count=2,
    )

    agent.handle_message(
        session,
        "我准备好了",
    )

    agent.handle_message(
        session,
        "RAG 是通过检索外部知识，再交给 LLM 生成答案以降低幻觉。",
    )

    response = agent.handle_message(
        session,
        "Prompt Engineering 是通过设计提示词来引导模型产生更好输出的方法。",
    )

    assert session.question_count == 2
    assert session.status == InterviewStatus.COMPLETED
    assert response == "本次面试结束，感谢你的参与。"
    assert session.history[-1] == {
        "role": "assistant",
        "content": response,
    }


def test_cancel_works_before_and_during_an_interview(make_agent):
    agent = make_agent()

    session = InterviewSession(session_id="test_005")

    response = agent.handle_message(
        session,
        "取消面试",
    )

    assert session.status == InterviewStatus.CANCELLED
    assert response == "本次面试已取消。"
    assert session.history == [
        {"role": "user", "content": "取消面试"},
        {"role": "assistant", "content": response},
    ]

    active_session = InterviewSession(session_id="test_006")

    agent.handle_message(
        active_session,
        "我准备好了",
    )

    response = agent.handle_message(
        active_session,
        "结束",
    )

    assert active_session.status == InterviewStatus.CANCELLED
    assert response == "本次面试已取消。"


def test_structured_evaluation_is_saved():
    llm = FakeLLMClient(
        {
            "decision": "follow_up",
            "score": 4,
            "reason": "回答过于简略",
            "missing_points": ["生成过程", "幻觉问题"],
        }
    )

    agent = InterviewAgent(llm)
    session = InterviewSession(session_id="test")

    agent.handle_message(session, "开始面试")
    agent.handle_message(session, "RAG 就是搜索资料。")

    assert session.last_evaluation is not None
    assert session.last_evaluation["score"] == 4
    assert session.last_evaluation["decision"] == "follow_up"