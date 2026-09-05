AI Interview Agent
一个面向 AI 应用开发岗位的工程化 AI 技术面试模拟 Agent，基于 LangGraph、FastAPI、Gemini、React、SSE、MCP、Tool Calling、SQLite 和 Docker 构建。

AI Interview Agent 是一个全栈 AI 应用，用于模拟 AI 应用开发相关技术岗位的面试过程。
本项目并不是简单的 LLM Chatbot，而是将一次完整的技术面试建模为一个有状态的 Agent Workflow，通过显式的领域状态、Agent 编排、结构化评估、Tool Calling、持久化、流式响应和 Web 前端共同实现完整的面试流程。
✨ 核心功能
面试流程
- 创建面试 Session
- 开始技术面试
- AI 自动提出技术问题
- 接收候选人回答
- 使用结构化输出评价回答
- 根据回答决定是否追问
- 自动进入下一道问题
- 记录问题数量和追问数量
- 完成或取消面试
AI / Agent 能力
- 基于 LangGraph 的 Agent Workflow
- 用户意图识别
- 基于 Pydantic 的 Structured Output
- Gemini 驱动的回答评价
- LLM Streaming
- Tool Calling
- 通过 Tool 进行面试题选择
- MCP Client / Server
- 统一的 LLM Client 抽象层
Backend
- FastAPI
- REST API
- Server-Sent Events（SSE）
- SQLite 持久化
- SQLAlchemy
- Session Recovery
- Domain State Machine
- 异常处理
Frontend
- React
- TypeScript
- Vite
- 面试回答流式显示
- 基于 Session 的面试界面
Deployment
- Docker
- Docker Compose
- Frontend Multi-stage Build
- Nginx Reverse Proxy
- SQLite Persistent Volume
- 前后端容器分离
🏗️ 系统架构
                    ┌──────────────────────┐
                    │      React UI        │
                    │  TypeScript + Vite   │
                    └──────────┬───────────┘
                               │
                               │ HTTP / SSE
                               ▼
                    ┌──────────────────────┐
                    │       Nginx          │
                    │    Reverse Proxy     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │      REST + SSE      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Interview Agent    │
                    │      LangGraph       │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ Intent      │   │ Evaluation  │   │ Question    │
      │ Detection   │   │ + Structured│   │ Tool        │
      │             │   │ Output      │   │             │
      └─────────────┘   └─────────────┘   └──────┬──────┘
                                                  │
                                                  ▼
                                         ┌────────────────┐
                                         │  Question Bank │
                                         └────────────────┘

                    ┌──────────────────────┐
                    │      Gemini LLM      │
                    │                      │
                    │ Text Generation      │
                    │ Structured Output    │
                    │ Streaming            │
                    │ Tool Calling         │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │       SQLite         │
                    │                      │
                    │ Interview Sessions  │
                    │ History              │
                    │ Evaluation Results   │
                    └──────────────────────┘
🔄 面试状态机
项目没有完全依赖 LLM 的隐式行为，而是通过显式状态机管理面试生命周期。
CREATED
   │
   │ START_INTERVIEW
   ▼
ASKING
   │
   │ QUESTION_SENT
   ▼
WAITING_FOR_ANSWER
   │
   │ ANSWER_RECEIVED
   ▼
EVALUATING
   │
   ├────────────── FOLLOW_UP_DECIDED ──────────────┐
   │                                               ▼
   │                                          FOLLOW_UP
   │                                               │
   │                                               │ FOLLOW_UP_SENT
   │                                               ▼
   │                                      WAITING_FOR_ANSWER
   │
   └──────────── NEXT_QUESTION_DECIDED ────────────┐
                                                   ▼
                                            NEXT_QUESTION
                                                   │
                                                   │ NEXT_QUESTION_READY
                                                   ▼
                                                ASKING
通过显式的 State 和 Event，可以让面试流程更加：
- 可控
- 可测试
- 可维护
- 容易扩展
🤖 Agent Workflow
Agent Runtime 使用 LangGraph 构建。
简化后的流程：
User Message
     │
     ▼
Intent Detection
     │
     ├── Start Interview
     │
     ├── Answer Question
     │
     ├── Cancel
     │
     └── Unknown
             │
             ▼
        Receive Answer
             │
             ▼
       Evaluate Answer
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
   Follow-up   Next Question
       │           │
       ▼           ▼
   Stream LLM   Tool Calling
                   │
                   ▼
             Question Bank
系统将以下职责进行分离：
Domain
Agent
Graph
LLM
Tools
Persistence
API
Frontend
避免将整个面试逻辑集中在一个 Chatbot 或 API Endpoint 中。
🧠 Structured Output
回答评价使用 Pydantic 定义结构化模型。
评价结果包含：
decision
score
reason
missing_points
例如：
{
  "decision": "follow_up",
  "score": 6,
  "reason": "回答包含基本概念，但没有完整解释 RAG 的检索流程。",
  "missing_points": [
    "Embedding generation",
    "Vector similarity search",
    "Context injection"
  ]
}
应用逻辑直接基于结构化结果判断：
follow_up
     │
     ▼
继续追问

next_question
     │
     ▼
进入下一题
而不是依赖字符串解析 LLM 的自然语言回答。
🔧 Tool Calling
下一道面试题的选择通过专门的 Tool 完成：
get_interview_question(
    topic,
    difficulty,
    excluded_questions
)
Tool 可以：
- 根据 Topic 选择问题
- 根据 Difficulty 选择问题
- 排除已经问过的问题
因此，问题选择逻辑并不需要全部写进 Prompt。
整体流程：
LLM
 │
 │ Tool Call
 ▼
get_interview_question
 │
 ▼
Question Bank
 │
 ▼
Tool Result
 │
 ▼
LLM
 │
 ▼
Next Interview Question
🔌 MCP
项目包含 MCP Client / Server 实现，用于实践 Agent 与外部能力之间的标准化连接方式。
MCP 层与核心 Interview Domain 保持分离，使外部能力可以在不直接耦合领域模型的情况下进行扩展。
⚡ Streaming
面试官的回答通过 Server-Sent Events（SSE）从后端实时传输到前端。
Gemini
  │
  │ token stream
  ▼
Interview Agent
  │
  ▼
FastAPI
  │
  │ SSE
  ▼
Nginx
  │
  ▼
React
  │
  ▼
Incremental UI Update
前端接收类似以下 SSE Event：
event: token
data: {"content":"..."}

event: done
data: {"status":"..."}
因此用户无需等待完整 LLM Response 生成完成，就可以看到面试官逐步输出的内容。
💾 数据持久化
面试 Session 使用以下技术进行持久化：
- SQLite
- SQLAlchemy
- Repository Pattern
Session 保存的信息包括：
session_id
status
target_question_count
question_count
current_question
current_answer
follow_up_count
history
last_evaluation
这样面试状态不会完全依赖进程内存，可以支持已有 Session 的恢复。
🌐 API
Health Check
GET /health
返回：
{
  "status": "ok"
}
创建 Session
POST /sessions
请求示例：
{
  "target_question_count": 5
}
获取 Session
GET /sessions/{session_id}
发送消息
POST /sessions/{session_id}/messages
请求示例：
{
  "message": "什么是 RAG？"
}
Streaming Message
POST /sessions/{session_id}/messages/stream
该接口通过 SSE 返回：
- token
- done
- error
🖥️ Frontend
前端使用：
- React
- TypeScript
- Vite
Frontend 通过：
/api/*
访问 Backend API。
Docker 部署时由 Nginx 将：
/api/*
转发到 FastAPI Backend。
因此浏览器只需要访问一个 Origin：
Browser
   │
   ▼
Nginx
 ┌─┴───────────────┐
 │                 │
 ▼                 ▼
Frontend          /api/*
                    │
                    ▼
                 FastAPI
🐳 Docker
项目支持通过 Docker Compose 启动完整应用。
                 Docker Compose
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   Backend Container         Frontend Container
   Python + FastAPI           Nginx + React
          │                         │
          │                         │
          └──────────┬──────────────┘
                     │
                     ▼
              Persistent Volume
                     │
                     ▼
                 SQLite DB
启动
创建 .env：
GEMINI_API_KEY=your_gemini_api_key
然后执行：
docker compose up --build
应用：
http://localhost
Backend Health Check：
http://localhost:8000/health
通过 Nginx：
http://localhost/api/health
停止
docker compose down
SQLite 数据保存在 Docker Volume：
interview_data
因此数据库不会随着 Backend Container 删除而消失。
💻 本地开发
Backend
创建 Python Virtual Environment：
python -m venv .venv
Windows：
.venv\Scripts\Activate.ps1
macOS / Linux：
source .venv/bin/activate
安装依赖：
pip install -r requirements.txt
创建 .env：
GEMINI_API_KEY=your_gemini_api_key
启动 Backend：
uvicorn app.main:app --reload
Backend：
http://127.0.0.1:8000
API Documentation：
http://127.0.0.1:8000/docs
Frontend
cd frontend
npm install
npm run dev
Frontend：
http://localhost:5173
🧪 测试
项目使用 pytest。
运行本地测试：
python -m pytest -m "not integration"
运行全部测试：
python -m pytest
需要调用外部 LLM API 的测试单独标记为：
@pytest.mark.integration
这样本地测试不会因为外部 API 的可用性、Quota 或网络问题而全部受到影响。
📁 项目结构
AI-Interview-Agent/
│
├── app/
│   ├── agent/
│   │   ├── evaluator.py
│   │   ├── intent_detector.py
│   │   ├── interview_agent.py
│   │   ├── models.py
│   │   └── response_generator.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── domain/
│   │   ├── events.py
│   │   ├── session.py
│   │   ├── state_machine.py
│   │   └── states.py
│   │
│   ├── graph/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── state.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── fake.py
│   │   └── gemini_client.py
│   │
│   ├── mcp_client/
│   │   └── client.py
│   │
│   ├── mcp_server/
│   │   └── server.py
│   │
│   ├── tools/
│   │   ├── question_tool.py
│   │   ├── registry.py
│   │   └── tools.py
│   │
│   ├── api_models.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   ├── test_repository.py
│   ├── test_session.py
│   ├── test_session_persistence.py
│   ├── test_state_machine.py
│   ├── test_structured_output.py
│   └── test_tool_calling.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .dockerignore
├── .gitignore
└── README.md
🛠️ 技术栈
Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Uvicorn
AI / Agent
- Google Gemini
- LangGraph
- Structured Output
- Tool Calling
- MCP
Frontend
- React
- TypeScript
- Vite
Infrastructure
- Docker
- Docker Compose
- Nginx
Testing
- pytest
🎯 工程化亮点
本项目重点关注的是 AI Application Engineering，而不仅仅是 Prompt Engineering。
1. 显式 Domain Modeling
Interview Status 和 Event 使用独立的 Domain Model 表示。
这样可以让面试流程保持确定性，并且方便测试。
2. Separation of Concerns
项目将系统拆分为：
Domain
Agent
Graph
LLM
Tools
Persistence
API
Frontend
而不是把所有业务逻辑集中在单个 API Endpoint 中。
3. LLM Abstraction
LLM 通过统一的 Client Protocol 提供：
generate()
generate_structured()
generate_stream()
generate_with_tools()
generate_with_tools_stream()
降低 Agent Runtime 与具体 LLM Provider 之间的耦合。
4. Structured Decision Making
Evaluation 使用 Typed Structured Output。
应用逻辑不需要通过字符串解析来判断 LLM 的最终决策。
5. Stateful Agent Runtime
使用 LangGraph 将面试流程建模为显式的 Nodes 和 Transitions。
6. Tool-Based Capability
面试题选择通过 Tool 实现，而不是将所有题目选择逻辑写进 Prompt。
7. Persistent Sessions
通过 Repository Layer + SQLite 保存 Interview Session。
8. Real-Time UX
通过 SSE 将 LLM Streaming 与 React UI 连接起来。
9. Containerized Deployment
Frontend 与 Backend 分别构建 Container，并通过 Docker Compose 进行编排。
📈 开发路线
项目按照工程化方式逐阶段完成。
Phase 0 — Business Modeling
- Interview Session
- Interview Lifecycle
- State Machine Design
Phase 1 — Domain Core
- Status
- Events
- Session
- State Machine
- Domain Tests
Phase 2 — Agent Runtime
- Intent Detection
- Answer Evaluation
- Follow-up Logic
- Interview Loop
Phase 3 — Real LLM
- Gemini Integration
- Structured Output
- LLM Abstraction
Phase 4 — API & Streaming
- FastAPI
- Session API
- SSE Streaming
Phase 5 — Persistence
- SQLite
- SQLAlchemy
- Repository Pattern
- Session Recovery
- Exception Handling
Phase 6 — Agent Engineering
- LangGraph
- MCP
- Tool Calling
- Question Selection Tool
Phase 7 — Productization
- React Frontend
- Docker
- Docker Compose
- Nginx Reverse Proxy
- GitHub / Project Documentation
- Final Project Polish
⚠️ API 可用性
项目使用 Gemini API 执行真实的 LLM 推理。
实际运行过程中可能受到以下因素影响：
- API Availability
- Rate Limits
- Quota
- Temporary Provider Errors
因此，项目将外部 LLM Integration Tests 与本地测试分离。
运行完整 AI 面试流程需要有效的 Gemini API Key。
🚧 后续改进方向
未来可以进一步加入：
- 用户认证
- 多用户 Session
- 更完整的面试题库
- 基于 RAG 的知识检索
- 自适应面试难度
- 更完善的回答评价体系
- Interview Analytics Dashboard
- PostgreSQL Production Persistence
- Redis Session / Streaming Infrastructure
- Background Job Processing
- Production Observability
- Automated Deployment
- Cloud Hosting
📌 项目状态
AI Interview Agent 是一个以 AI Application Engineering 为核心的全栈项目。
当前已经覆盖：
- Domain Modeling
- Stateful Agent Orchestration
- LLM Integration
- Structured Output
- Tool Calling
- MCP
- REST API
- SSE Streaming
- Persistence
- React Frontend
- Docker Deployment
项目重点展示实际 AI 应用开发中的工程能力，而不仅仅是 Prompt Engineering。
License
本项目目前主要用于学习、工程实践以及个人 Portfolio 展示。