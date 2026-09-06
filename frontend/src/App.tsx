
import { useState } from "react";
import "./App.css";

const API_BASE_URL = "/api";

type Message = {
  role: "interviewer" | "candidate";
  content: string;
};

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startInterview() {
    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          target_question_count: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `创建面试 Session 失败（HTTP ${response.status}）`,
        );
      }

      const data = await response.json();

      if (!data.session_id) {
        throw new Error("服务器没有返回 session_id");
      }

      setSessionId(data.session_id);
      setMessages([]);
      setCompleted(false);

      await sendStartInterview(data.session_id);
    } catch (err) {
      setSessionId(null);
      setMessages([]);

      setError(
        err instanceof Error
          ? err.message
          : "启动面试失败，请稍后重试。",
      );
    } finally {
      setLoading(false);
    }
  }

  async function sendStartInterview(currentSessionId: string) {
    await sendStreamingRequest(
      `${API_BASE_URL}/sessions/${currentSessionId}/start/stream`,
      null,
    );
  }

  async function sendStreamingRequest(
    endpoint: string,
    message: string | null,
  ) {
    let interviewerMessageIndex = -1;

    try {
      const response = await fetch(
        endpoint,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: message === null ? undefined : JSON.stringify({
            message,
          }),
        },
      );

      if (!response.ok) {
        let detail = "";

        try {
          const data = await response.json();

          if (typeof data.detail === "string") {
            detail = data.detail;
          }
        } catch {
          // 后端可能返回非 JSON 错误响应，忽略解析失败。
        }

        if (response.status === 404) {
          throw new Error(
            detail || "面试 Session 不存在，请重新开始面试。",
          );
        }

        if (response.status === 429) {
          throw new Error(
            detail ||
              "AI 服务当前达到使用限制，请稍后再试。",
          );
        }

        throw new Error(
          detail ||
            `发送消息失败（HTTP ${response.status}）`,
        );
      }

      if (!response.body) {
        throw new Error("服务器没有返回 Streaming 数据。");
      }

      /*
       * 先创建一个空的 Interviewer 消息。
       * 后续收到 chunk 后不断更新它。
       */
      setMessages((previous) => {
        interviewerMessageIndex = previous.length;

        return [
          ...previous,
          {
            role: "interviewer",
            content: "",
          },
        ];
      });

      const reader = response.body.getReader();
const decoder = new TextDecoder();

let receivedContent = false;
let completedByDone = false;
let buffer = "";

function appendInterviewerContent(content: string) {
  if (!content) {
    return;
  }

  receivedContent = true;

  setMessages((previous) =>
    previous.map((item, index) =>
      index === interviewerMessageIndex
        ? {
            ...item,
            content: item.content + content,
          }
        : item,
    ),
  );
}

function processSseBuffer() {
  const events = buffer.split("\n\n");

  buffer = events.pop() ?? "";

  for (const eventBlock of events) {
    const lines = eventBlock.split("\n");

    let eventType = "";
    let data = "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        data += line.slice(5).trim();
      }
    }

    if (!data) {
      continue;
    }

    if (eventType === "token") {
      try {
        const payload = JSON.parse(data);

        if (typeof payload.content === "string") {
          appendInterviewerContent(payload.content);
        }
      } catch {
        // 忽略无法解析的 SSE token。
      }
    }

    if (eventType === "done") {
      try {
        const payload = JSON.parse(data);

        if (payload.status === "completed") {
          completedByDone = true;
          setCompleted(true);
        }
      } catch {
        // done 数据异常时不影响已经收到的内容。
      }
    }

    if (eventType === "error") {
      try {
        const payload = JSON.parse(data);

        throw new Error(
          payload.message || "AI 服务请求失败。",
        );
      } catch (err) {
        if (err instanceof Error) {
          throw err;
        }

        throw new Error("AI 服务请求失败。");
      }
    }
  }
}

while (true) {
  const { value, done } = await reader.read();

  if (done) {
    break;
  }

  buffer += decoder.decode(value, {
    stream: true,
  });

  processSseBuffer();
}

buffer += decoder.decode();

if (buffer.trim()) {
  processSseBuffer();
}

      /*
       * 如果 HTTP 请求成功，但是服务器没有返回任何内容，
       * 删除刚才创建的空消息，避免 UI 留下空气泡。
       */
      if (!receivedContent && !completedByDone) {
        setMessages((previous) =>
          previous.filter(
            (_, index) => index !== interviewerMessageIndex,
          ),
        );

        throw new Error(
          "AI 没有返回任何内容，请稍后重试。",
        );
      }
    } catch (err) {
      /*
       * 如果 Streaming 过程中发生异常，
       * 删除尚未完成的 Interviewer 空消息。
       */
      if (interviewerMessageIndex >= 0) {
        setMessages((previous) =>
          previous.filter(
            (_, index) => index !== interviewerMessageIndex,
          ),
        );
      }

      throw new Error(
        err instanceof Error
          ? err.message
          : "AI 服务请求失败，请稍后重试。",
      );
    }
  }

  async function sendMessage(
    currentSessionId: string,
    message: string,
  ) {
    await sendStreamingRequest(
      `${API_BASE_URL}/sessions/${currentSessionId}/messages/stream`,
      message,
    );
  }

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !sessionId ||
      !input.trim() ||
      loading ||
      completed
    ) {
      return;
    }

    const answer = input.trim();

    setInput("");
    setError(null);
    setLoading(true);

    /*
     * 先把候选人的回答加入聊天记录。
     */
    setMessages((previous) => [
      ...previous,
      {
        role: "candidate",
        content: answer,
      },
    ]);

    try {
      await sendMessage(sessionId, answer);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "发送回答失败，请稍后重试。",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Interview Agent</h1>
          <p>AI 技术面试模拟</p>
        </div>

        {!sessionId && (
          <button
            className="start-button"
            onClick={startInterview}
            disabled={loading}
          >
            {loading ? "正在启动..." : "开始面试"}
          </button>
        )}
      </header>

      <main className="interview-container">
        {!sessionId ? (
          <div className="welcome">
            <h2>准备好开始面试了吗？</h2>

            <p>
              这是一个面向 AI 应用开发岗位的技术面试 Agent。
            </p>

            <p>
              面试过程中，AI 会根据你的回答进行评价，
              必要时进行追问。
            </p>

            <button
              className="start-large-button"
              onClick={startInterview}
              disabled={loading}
            >
              {loading ? "正在启动..." : "开始面试"}
            </button>

            {error && (
              <div className="error">
                {error}
              </div>
            )}
          </div>
        ) : (
          <>
            <div className="messages">
              {messages.map((message, index) => {
                const isStreaming =
                  loading &&
                  message.role === "interviewer" &&
                  index === messages.length - 1;

                return (
                  <div
                    key={index}
                    className={`message-row ${message.role}`}
                  >
                    <div className="message-label">
                      {message.role === "interviewer"
                        ? "Interviewer"
                        : "You"}
                    </div>

                    <div className="message-bubble">
                      {message.content}

                      {isStreaming && (
                        <span className="streaming-cursor">
                          ▌
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}

              {loading &&
                messages.length > 0 &&
                messages[messages.length - 1].role ===
                  "candidate" && (
                  <div className="message-row interviewer">
                    <div className="message-label">
                      Interviewer
                    </div>

                    <div className="message-bubble">
                      <span className="thinking">
                        AI 正在思考...
                      </span>
                    </div>
                  </div>
                )}

              {completed && (
                <div className="completed-message">
                  🎉 本次面试已经完成。
                </div>
              )}
            </div>

            <form
              className="input-area"
              onSubmit={handleSubmit}
            >
              <textarea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                placeholder={
                  completed
                    ? "本次面试已经完成"
                    : loading
                      ? "AI 正在思考，请稍候..."
                      : "输入你的回答..."
                }
                disabled={loading || completed}
                rows={3}
              />

              <button
                type="submit"
                disabled={
                  loading ||
                  completed ||
                  !input.trim()
                }
              >
                {loading ? "AI 思考中..." : "发送"}
              </button>
            </form>

            {error && (
              <div className="error">
                {error}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
