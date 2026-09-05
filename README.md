# AI Interview Agent

An engineering-oriented AI technical interview simulator built with **LangGraph, FastAPI, Gemini, React, SSE, MCP, Tool Calling, SQLite, and Docker**.

AI Interview Agent is a full-stack AI application designed to simulate technical interviews for AI application engineering roles.

Instead of treating the system as a simple LLM chatbot, the project models an interview as a **stateful workflow** with explicit domain states, agent orchestration, structured evaluation, tool calling, persistence, streaming responses, and a web interface.

## ✨ Features

### Interview Workflow

- Create an interview session
- Start a technical interview
- Ask AI engineering questions
- Receive candidate answers
- Evaluate answers with structured output
- Decide whether to ask a follow-up question
- Move to the next question
- Track question and follow-up counts
- Complete or cancel an interview

### AI / Agent Capabilities

- LangGraph-based agent workflow
- Intent detection
- Structured answer evaluation
- Follow-up question generation
- Question Bank tool
- Tool Calling
- MCP integration
- Gemini LLM integration
- Streaming LLM responses

### Backend

- FastAPI
- REST API
- Server-Sent Events (SSE)
- SQLite persistence
- Session recovery
- Exception handling
- Repository pattern
- Pydantic models

### Frontend

- React
- TypeScript
- Vite
- Real-time SSE streaming
- Interview session UI
- Conversation history
- Interview status display

### Deployment

- Docker
- Docker Compose
- Multi-stage frontend build
- Nginx reverse proxy
- Persistent SQLite volume
- Backend / frontend container separation

---

## 🏗️ Architecture

```mermaid
flowchart TB
    UI["React UI<br/>TypeScript + Vite"]
    NGINX["Nginx<br/>Reverse Proxy"]
    API["FastAPI<br/>REST + SSE"]
    AGENT["Interview Agent<br/>LangGraph"]
    INTENT["Intent Detection"]
    EVAL["Answer Evaluation<br/>Structured Output"]
    TOOL["Question Bank<br/>Tool Calling"]
    MCP["MCP"]
    LLM["Gemini LLM"]
    DB["SQLite<br/>Persistent Storage"]

    UI --> NGINX
    NGINX --> API
    API --> AGENT

    AGENT --> INTENT
    AGENT --> EVAL
    AGENT --> TOOL
    AGENT --> MCP
    AGENT --> LLM

    EVAL --> LLM
    TOOL --> LLM
    MCP --> LLM

    API --> DB
```

The system is organized into several layers:

```text
Frontend
   ↓
Nginx
   ↓
FastAPI
   ↓
Interview Agent
   ↓
LangGraph
   ↓
LLM / Structured Output / Tools / MCP
   ↓
SQLite
```

This separation keeps domain logic, agent orchestration, infrastructure, and presentation concerns relatively independent.
🔄 Interview State Machine
The interview lifecycle is modeled as an explicit state machine rather than a collection of loosely connected LLM calls.
```mermaid
stateDiagram-v2
    [*] --> CREATED

    CREATED --> ASKING: START_INTERVIEW
    ASKING --> WAITING_FOR_ANSWER: QUESTION_SENT
    WAITING_FOR_ANSWER --> EVALUATING: ANSWER_RECEIVED

    EVALUATING --> FOLLOW_UP: FOLLOW_UP_DECIDED
    EVALUATING --> NEXT_QUESTION: NEXT_QUESTION_DECIDED

    FOLLOW_UP --> WAITING_FOR_ANSWER: FOLLOW_UP_SENT

    NEXT_QUESTION --> ASKING: NEXT_QUESTION_READY
    NEXT_QUESTION --> COMPLETED: QUESTION_LIMIT_REACHED

    CREATED --> CANCELLED: CANCEL
    ASKING --> CANCELLED: CANCEL
    WAITING_FOR_ANSWER --> CANCELLED: CANCEL
    EVALUATING --> CANCELLED: CANCEL
    FOLLOW_UP --> CANCELLED: CANCEL
    NEXT_QUESTION --> CANCELLED: CANCEL
```
Core interview states:
- CREATED
- ASKING
- WAITING_FOR_ANSWER
- EVALUATING
- FOLLOW_UP
- NEXT_QUESTION
- COMPLETED
- CANCELLED
The state machine makes interview transitions explicit and testable.
🤖 Agent Workflow
LangGraph coordinates the execution flow of the interview.
```mermaid
flowchart TD
    START["User Message"]
    INTENT["Detect Intent"]

    START --> INTENT

    INTENT --> START_NODE["Start Interview"]
    INTENT --> ANSWER["Receive Answer"]
    INTENT --> CANCEL["Cancel Interview"]
    INTENT --> UNKNOWN["Unknown Message"]

    ANSWER --> EVALUATE["Evaluate Answer"]

    EVALUATE --> FOLLOW["Follow-up"]
    EVALUATE --> NEXT["Next Question"]

    FOLLOW --> WAIT["Wait for Answer"]
    NEXT --> QUESTION["Generate Next Question"]

    QUESTION --> LIMIT{"Question Limit?"}

    LIMIT -->|No| ASK["Ask Question"]
    LIMIT -->|Yes| COMPLETE["Complete Interview"]

    START_NODE --> ASK
    ASK --> WAIT

    CANCEL --> END["Terminal Response"]
    UNKNOWN --> END
    COMPLETE --> END
```
LangGraph handles agent orchestration, while the domain state machine defines valid interview state transitions.
This allows the project to combine:
- Deterministic domain rules
- Graph-based orchestration
- LLM reasoning
- Tool execution
- Persistent session state
🧠 Structured Output
Answer evaluation uses structured LLM output instead of relying on free-form text parsing.
The evaluator produces:
decision
score
reason
missing_points
Example:

```json
{
  "decision": "follow_up",
  "score": 7,
  "reason": "The answer demonstrates the basic concept but lacks implementation details.",
  "missing_points": [
    "retrieval strategy",
    "chunking considerations"
  ]
}
```

The structured evaluation result is then used by the agent workflow to determine the next action.

Conceptually:

```text
Evaluate Answer
       ↓
   Decision
    ↙     ↘
Follow-up  Next Question
```
🛠️ Tool Calling
The agent can use a Question Bank Tool to retrieve interview questions.
The Question Bank considers previously asked questions when selecting the next question.
The overall flow is:

```text
Interview Agent
      ↓
Question Bank Tool
      ↓
Question Selection
      ↓
Next Interview Question
```

This demonstrates how an LLM agent can combine reasoning with deterministic application tools instead of putting all question-selection logic inside prompts.
🔌 MCP
The project includes an MCP client/server implementation for practicing the Model Context Protocol.
The MCP layer demonstrates how external capabilities can be exposed as tools that an agent can interact with.
Practice areas include:
- MCP client/server architecture
- Tool discovery
- Tool invocation
- Agent-to-tool interaction
🌊 Streaming
The backend supports Server-Sent Events (SSE) for real-time responses.
```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant Agent as Interview Agent
    participant LLM as Gemini LLM

    UI->>API: POST /messages/stream
    API->>Agent: Handle message
    Agent->>LLM: Generate stream

    loop Streaming
        LLM-->>Agent: Token
        Agent-->>API: Chunk
        API-->>UI: SSE token
    end

    API-->>UI: SSE done
```
The complete streaming pipeline includes:
- Gemini streaming
- Agent streaming
- FastAPI SSE
- React SSE parsing
Users can therefore receive generated content incrementally instead of waiting for the complete response.
💾 Persistence
Interview sessions are persisted using SQLite.
Persistent information includes:
- Session ID
- Interview status
- Target question count
- Question count
- Current question
- Current answer
- Follow-up count
- Interview history
- Latest evaluation
The application uses a Repository Layer to separate persistence logic from the rest of the application.

```text
FastAPI
   ↓
Repository
   ↓
SQLAlchemy
   ↓
SQLite
```

This allows interview sessions to be recovered after the application process restarts.
🔌 API
Health Check
GET /health
Example response:
{
  "status": "ok"
}
Create Interview Session
POST /sessions
Example request:
{
  "target_question_count": 5
}
Get Interview Session
GET /sessions/{session_id}
Send Message
POST /sessions/{session_id}/messages
Send Streaming Message
POST /sessions/{session_id}/messages/stream
The streaming endpoint returns Server-Sent Events.
🖥️ Frontend
The frontend is implemented with:
- React
- TypeScript
- Vite
- SSE
The frontend communicates with the backend through the /api path.
In the Docker environment, Nginx acts as the reverse proxy between the browser and backend container.
```mermaid
flowchart LR
    B["Browser"]
    N["Nginx :80"]
    A["FastAPI :8000"]

    B --> N
    N --> A
```
🐳 Docker
The project provides Docker configuration for both backend and frontend.
Backend
The backend image uses:
- Python 3.12
- FastAPI
- Uvicorn
Frontend
The frontend uses a multi-stage Docker build:
Node.js
   ↓
npm build
   ↓
Static Files
   ↓
Nginx
Docker Compose
The complete application can be started with:
docker compose up --build
Container architecture:
```mermaid
flowchart TB
    B["Browser"]
    F["Frontend Container<br/>Nginx :80"]
    BE["Backend Container<br/>FastAPI :8000"]
    DB["SQLite<br/>Persistent Volume"]

    B --> F
    F -->|"/api"| BE
    BE --> DB
```
🚀 Local Development
Backend
Create a Python virtual environment:
python -m venv .venv
Windows:
.venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
Configure environment variables in .env.
Start the backend:
uvicorn app.main:app --reload
The backend will be available at:
http://localhost:8000
Frontend
Navigate to the frontend directory:
cd frontend
Install dependencies:
npm install
Start the development server:
npm run dev
The frontend will normally be available at:
http://localhost:5173
🧪 Testing
The project includes unit and integration tests covering areas such as:
- Domain state machine
- Interview session
- Agent behavior
- API
- Persistence
- Repository
- Structured output
- Gemini client
- Streaming
- Tool Calling
Run the non-integration test suite:
python -m pytest -m "not integration"
Integration tests that depend on external LLM services may require valid API credentials and available model quota.
## 📁 Project Structure

```text
AI-Interview-Agent/
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
│   │   ├── repository.py
│   │   └── init_db.py
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
│   ├── package.json
│   └── vite.config.ts
│
├── tests/
├── docs/
│   └── image/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── README.zh-CN.md
└── .dockerignore
```
🧰 Tech Stack
## 🧰 Tech Stack

| Category | Technology |
|---|---|
| Language | Python, TypeScript |
| Backend | FastAPI |
| Agent Framework | LangGraph |
| LLM | Google Gemini |
| Structured Output | Pydantic |
| Tool Calling | Gemini Tool Calling |
| Protocol | MCP |
| Streaming | Server-Sent Events |
| Frontend | React |
| Frontend Tooling | Vite |
| Database | SQLite |
| ORM | SQLAlchemy |
| Containerization | Docker |
| Reverse Proxy | Nginx |
| Testing | Pytest |

🎯 Engineering Highlights
This project focuses on AI application engineering rather than simply calling an LLM API.
1. Explicit Domain Modeling
Interview states and events are modeled explicitly, making the core workflow deterministic and testable.
2. Agent Orchestration
LangGraph manages the execution flow between intent detection, evaluation, follow-up generation, question generation, completion, and cancellation.
3. Structured LLM Output
Pydantic models provide a typed boundary between LLM responses and application logic.
4. Tool-Augmented Agent
The Question Bank is exposed as a callable tool instead of embedding all question-selection logic inside prompts.
5. MCP Practice
The project contains an MCP client/server implementation to explore standardized tool integration.
6. Real-Time Streaming
The complete streaming path works from the LLM through the agent and FastAPI SSE endpoint to the React frontend.
7. Persistence and Recovery
Interview sessions survive application restarts through SQLite persistence.
8. Containerized Deployment
Frontend and backend are separated into containers and connected through Nginx and Docker Compose.
📈 Development Roadmap
The project was developed through the following engineering phases:
- Phase 0 — Business Modeling / Interview Session / State Machine
- Phase 1 — Domain Core
- Phase 2 — Agent Runtime
- Phase 3 — Real LLM + Structured Output
- Phase 4 — FastAPI + Streaming + Session API
- Phase 5 — Persistence + Session Recovery + Exception Handling
- Phase 6 — LangGraph + MCP + Tool Calling
- Phase 7 — Frontend + Docker + Deployment + GitHub/README Packaging
All planned phases are currently completed.
🔮 Future Improvements
Potential future extensions include:
- Authentication and user accounts
- PostgreSQL production database
- Redis-based session management
- More advanced interview scoring
- Resume-aware interview generation
- Difficulty adaptation based on candidate performance
- Interview report generation
- Observability and tracing
- Production cloud deployment
- CI/CD pipeline
- More MCP-based external tools
## 📌 Project Status

**Completed — Phase 0 through Phase 7**

The project currently provides a complete full-stack AI interview simulation system with:

- Domain Modeling
- State Machine
- LLM Integration
- Structured Output
- LangGraph
- Tool Calling
- MCP
- SSE Streaming
- Persistence
- React
- Docker

The project is designed as an engineering-oriented portfolio project for learning and demonstrating:

- AI application development
- Backend engineering
- LLM integration
- Agent orchestration
- Structured output
- Tool Calling
- MCP
- Streaming architecture
- Containerized deployment