# ProcureOps

> AI-powered procurement operations assistant built with LangGraph, FastAPI, RAG, MCP, Human-in-the-Loop approval, and RBAC.

ProcureOps is an AI-powered procurement assistant designed to simplify common procurement operations such as retrieving RFQ data, comparing quotations, searching vendors, retrieving procurement policies, and handling sensitive quotation approval workflows.

The application combines an **agentic workflow with deterministic business logic**, allowing the AI layer to understand user requests while keeping sensitive procurement operations controlled through authorization, validation, and Human-in-the-Loop (HITL) approval.

---

## 🚀 Key Features

- 🤖 **LangGraph Agent Workflow**
- 🧠 **Conversation and Long-Term Memory**
- 🔐 **JWT Authentication**
- 👥 **Role-Based Access Control (RBAC)**
- 🛡️ **Basic AI Guardrails**
- ✋ **Human-in-the-Loop (HITL)**
- 🔌 **MCP Tool Integration**
- 📚 **Retrieval-Augmented Generation (RAG)**
- 🗄️ **Live Procurement Data Retrieval**
- 🔎 **RFQ and Quotation Comparison**
- 🏢 **Vendor Search and Retrieval**
- ⚡ **Redis Integration**
- 🧪 **Automated Testing**
- 📊 **LLM-as-a-Judge Evaluation**
- 🔭 **LangSmith Observability**
- ⚡ **FastAPI Backend**
- ⚛️ **React Frontend**
- 🐘 **PostgreSQL**
- 🐳 **Dockerized Development Environment**

---

# 🏗️ Architecture

```mermaid
flowchart TD
    U[User] --> API[FastAPI API]

    API --> AGENT[ProcureOps Agent]

    AGENT --> G[Guardrail]
    G -->|Blocked| END1[End]

    G -->|Allowed| M[Memory Retrieval]
    M --> O[Operation Resolution]
    O --> C[Context Resolution]
    C --> H[Human-in-the-Loop]

    H -->|Sensitive Action| A[Action Execution]
    H -->|Normal Request| R[Router]

    A --> MU[Memory Update]

    R -->|LIVE_DATA| L[Live Data]
    R -->|KNOWLEDGE| RAG[RAG]
    R -->|GENERAL| GEN[General]

    L --> MU
    RAG --> MU
    GEN --> MU

    MU --> RESP[Response]
    RESP --> API
    API --> U

    L --> MCP[MCP Tools]
    MCP --> DB[(PostgreSQL)]

    RAG --> VS[(Vector Store)]
    RAG --> LLM[LLM]

    A --> DB
```

---

# 🔄 Agent Workflow

```mermaid
flowchart TD
    START([User Query]) --> GR[Guardrail]

    GR -->|Blocked| END1([End])
    GR -->|Allowed| MR[Memory Retrieval]

    MR --> OR[Operation Resolution]
    OR --> CR[Context Resolution]
    CR --> HITL[Human-in-the-Loop]

    HITL -->|Sensitive action<br/>Approved / Rejected| AE[Action Execution]
    HITL -->|Normal request| ROUTER[Router]

    AE --> MU[Memory Update]

    ROUTER -->|LIVE_DATA| LD[Live Data]
    ROUTER -->|KNOWLEDGE| RAG[RAG]
    ROUTER -->|GENERAL| GEN[General]

    LD --> MU
    RAG --> MU
    GEN --> MU

    MU --> RESP[Response]
    RESP --> END2([End])
```

---

# 🧩 Graph Nodes

| Node | Description |
|---|---|
| **Guardrail** | Validates the incoming user request and blocks unsafe, malicious, or prompt-injection attempts before they reach the main workflow. |
| **Memory Retrieval** | Retrieves relevant information from previous interactions to maintain conversational context and continuity. |
| **Operation Resolution** | Determines the procurement operation requested by the user, such as viewing quotations, comparing quotations, or approving/rejecting a quotation. |
| **Context Resolution** | Extracts and resolves entities required for the operation, including RFQ numbers, quotation IDs/numbers, vendor IDs/codes, and other relevant context. |
| **HITL** | Identifies sensitive procurement actions and pauses the workflow until an authorized human provides an approval or rejection decision. |
| **Action Execution** | Executes the authorized procurement action after validation, such as approving or rejecting a quotation and updating the database. |
| **Router** | Determines how the request should be handled based on its data access requirement. |
| **Live Data** | Retrieves current procurement information from the application database through the appropriate tools/MCP layer. |
| **RAG** | Retrieves relevant procurement policies and knowledge from the knowledge base to generate grounded responses. |
| **General** | Handles general procurement-related questions that do not require live database data or document retrieval. |
| **Memory Update** | Stores useful information from the current interaction for future context and conversations. |
| **Response** | Generates the final user-facing response. |

---

# 🔀 Request Routing

The agent classifies requests into three primary data access paths:

```text
                         User Query
                              │
                              ▼
                         AI Workflow
                              │
                              ▼
                           Router
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
               LIVE_DATA  KNOWLEDGE  GENERAL
                    │         │         │
                    ▼         ▼         ▼
                Database     RAG      LLM Response
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                       Memory Update
                              │
                              ▼
                           Response
```

### LIVE_DATA

Used when the user needs current procurement information.

Examples:

```text
Show quotations for RFQ-000036
```

```text
Find vendors with code VEN-001
```

```text
Compare quotations for RFQ-000036
```

The request is routed to the live-data node, which retrieves the required information through application tools/MCP.

---

### KNOWLEDGE

Used when the user asks questions about procurement policies or organizational knowledge.

Example:

```text
What is the policy for high-value procurement?
```

The request is routed to the RAG node.

The RAG pipeline:

```text
User Query
    ↓
Embedding
    ↓
Vector Search
    ↓
Relevant Documents
    ↓
LLM
    ↓
Grounded Response
```

---

### GENERAL

Used for general procurement questions that do not require live application data or retrieval from the knowledge base.

Example:

```text
What is an RFQ?
```

---

# ✋ Human-in-the-Loop

Sensitive procurement actions require explicit human intervention.

Currently, quotation approval and rejection are treated as sensitive operations.

Example:

```text
User
 │
 │ "Approve quotation QT-000005"
 ▼
Operation Resolution
 │
 ▼
Context Resolution
 │
 ▼
Authorization
 │
 ▼
HITL Interrupt
 │
 ├── APPROVE
 │
 └── REJECT
 │
 ▼
Action Execution
 │
 ▼
Database Update
 │
 ▼
Response
```

The workflow uses LangGraph's interrupt/resume mechanism to pause execution and wait for a human decision.

### Example HITL Request

```json
{
  "status": "awaiting_approval",
  "conversation_id": "hitl-api-001",
  "hitl_request": {
    "action": "APPROVE_QUOTATION",
    "quotation_id": 5,
    "quotation_number": "QT-000005",
    "message": "Human approval is required to approve the quotation."
  }
}
```

After the human decision, the same conversation is resumed.

```text
APPROVE / REJECT
       ↓
Resume Graph
       ↓
Action Execution
       ↓
Database Update
       ↓
Final Response
```

---

# 🔐 Authorization and RBAC

ProcureOps uses JWT authentication and role-based permissions.

Sensitive actions are checked before execution.

For example:

```text
User
 ↓
Authentication
 ↓
Active User Check
 ↓
Role Check
 ↓
Permission Check
 ↓
Resource Validation
 ↓
HITL
 ↓
Action Execution
```

Quotation approval and rejection require the corresponding permissions:

```text
approval:approve
approval:reject
```

The application also validates that:

- The user exists.
- The user account is active.
- The user has the required permission.
- The quotation exists.
- The quotation is in a valid state.
- The requested action is allowed for that quotation.

---

# 🔌 MCP Integration

ProcureOps uses the **Model Context Protocol (MCP)** to expose procurement capabilities as tools.

The MCP layer provides a standardized interface between the AI workflow and application capabilities.

### MCP Tools

| Tool | Purpose |
|---|---|
| `get_rfq_quotations` | Retrieve quotations associated with an RFQ |
| `compare_rfq_quotations` | Compare quotations for an RFQ |
| `get_vendor` | Retrieve vendor information |
| `search_vendors` | Search vendors |
| `approve_quotation` | Procurement quotation approval capability |
| `reject_quotation` | Procurement quotation rejection capability |

### MCP Flow

```text
Agent
  ↓
Operation
  ↓
MCP Tool Mapping
  ↓
MCP Client
  ↓
MCP Server
  ↓
Procurement Service
  ↓
PostgreSQL
```

The MCP layer keeps tool capabilities separate from the agent's reasoning workflow.

---

# 📚 RAG Pipeline

ProcureOps uses Retrieval-Augmented Generation for procurement policies and organizational knowledge.

```text
             User Question
                   │
                   ▼
              RAG Node
                   │
                   ▼
             Query Embedding
                   │
                   ▼
             Vector Search
                   │
                   ▼
          Relevant Documents
                   │
                   ▼
              LLM Generation
                   │
                   ▼
          Grounded Response
```

RAG is useful for questions such as:

```text
What is the approval policy for high-value procurement?
```

```text
What are the procurement rules for restricted data?
```

The system retrieves relevant policy information before generating the response.

---

# 🧠 Memory

ProcureOps maintains conversational context using two complementary memory mechanisms.

### Short-Term Conversation Memory

LangGraph checkpointing maintains state across requests using a conversation/thread identifier.

```text
Conversation ID
      ↓
LangGraph Checkpoint
      ↓
Previous State
      ↓
Current Request
```

This allows the agent to maintain context across multiple interactions.

Example:

```text
User:
Show quotations for RFQ-000036

Agent:
[Quotation information...]

User:
Compare them
```

The second request can use the active RFQ context from the conversation.

---

### Long-Term Memory

Useful information from interactions can be persisted and retrieved for future conversations.

```text
Interaction
    ↓
Memory Update
    ↓
Persistent Memory
    ↓
Future Conversation
    ↓
Memory Retrieval
```

Memory is scoped to the user/conversation context to avoid unnecessarily mixing information between users.

---

# 🛡️ Guardrails

Basic guardrails are applied before the request enters the main agent workflow.

The guardrail layer helps protect against:

- Prompt injection
- Instruction override attempts
- Unauthorized action requests
- Attempts to bypass approval workflows
- Unsafe agent instructions

Example:

```text
User Input
    ↓
Guardrail
    │
    ├── Unsafe → Block
    │
    └── Safe → Continue
```

Sensitive procurement actions are not allowed to bypass the authorization and HITL workflow through natural-language instructions.

---

# 📊 Evaluation

ProcureOps includes basic automated evaluation to measure agent response quality.

The evaluation combines deterministic checks with an LLM-based judge.

### Evaluation Dimensions

- Correctness
- Relevance
- Groundedness
- Overall quality

Example evaluation structure:

```json
{
  "correctness": 0.95,
  "relevance": 0.90,
  "groundedness": 0.95,
  "overall_quality": 0.93,
  "reasoning": "The response correctly identifies the quotations and provides relevant information."
}
```

The evaluation suite also tests scenarios such as:

- RFQ quotation retrieval
- Quotation comparison
- Guardrail blocking
- Prompt-injection attempts
- Approval bypass attempts
- RFQ-not-found scenarios

---

# 🔭 Observability

ProcureOps integrates with **LangSmith** for tracing and debugging the agent workflow.

The traces provide visibility into:

- LangGraph execution
- Individual nodes
- LLM calls
- Retrieval operations
- Tool execution
- Execution time
- Token usage
- Errors and failures

Example trace flow:

```text
LangGraph
   │
   ├── Guardrail
   ├── Memory Retrieval
   ├── Operation Resolution
   ├── Context Resolution
   ├── Router
   ├── Live Data / RAG
   ├── Memory Update
   └── Response
```

This makes it easier to understand agent behavior and identify performance bottlenecks.

---

# 🏢 Procurement Workflow

The application models a simplified procurement lifecycle.

```text
Purchase Request
       ↓
Approval
       ↓
RFQ Creation
       ↓
Vendor Selection
       ↓
RFQ Issued
       ↓
Vendor Quotations
       ↓
RFQ Closed
       ↓
Quotation Comparison
       ↓
Quotation Approval
       ↓
Quotation Accepted / Rejected
```

### Purchase Request

A Procurement Analyst creates and submits a Purchase Request.

```text
DRAFT
  ↓
SUBMITTED
  ↓
APPROVAL_PENDING
```

### RFQ

After the required approval, the Procurement Head can create an RFQ and invite vendors.

```text
RFQ DRAFT
    ↓
Add Vendors
    ↓
Issue RFQ
```

Once the RFQ is issued, the vendor list is frozen.

### Quotations

Vendors can submit quotations against issued RFQs.

```text
RFQ
 ↓
Vendor
 ↓
Quotation
 ↓
SUBMITTED
```

### Quotation Approval

Sensitive quotation approval is handled through the HITL workflow.

```text
SUBMITTED
    ↓
HITL
    ↓
APPROVE / REJECT
    ↓
ACCEPTED / REJECTED
```

---

# 💬 Example AI Queries

### Live Procurement Data

```text
Show quotations for RFQ-000036
```

```text
Compare quotations for RFQ-000036
```

```text
Find vendor VEN-001
```

```text
Search for active vendors
```

---

### Procurement Knowledge

```text
What is the policy for high-value procurement?
```

```text
What are the procurement approval rules?
```

```text
What is the policy for restricted data processing?
```

---

### Sensitive Actions

```text
Approve quotation QT-000005
```

```text
Reject quotation QT-000005
```

Sensitive requests trigger the HITL workflow instead of being executed immediately.


---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Agent Orchestration | LangGraph |
| LLM | Groq / LLM Provider |
| AI Framework | LangChain |
| Tool Protocol | MCP |
| RAG | Embeddings + Vector Store |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Cache / Supporting Infrastructure | Redis |
| Observability | LangSmith |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |

---

# 📁 Project Structure

```text
ProcureOps/
│
├── backend/
│   │
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/
│   │   │   │   ├── nodes/
│   │   │   │   │   ├── guardrail_node.py
│   │   │   │   │   ├── memory_node.py
│   │   │   │   │   ├── operation_resolution_node.py
│   │   │   │   │   ├── context_resolution_node.py
│   │   │   │   │   ├── hitl_node.py
│   │   │   │   │   ├── action_execution_node.py
│   │   │   │   │   ├── router_node.py
│   │   │   │   │   ├── live_data_node.py
│   │   │   │   │   ├── rag_node.py
│   │   │   │   │   ├── general_node.py
│   │   │   │   │   └── response_node.py
│   │   │   │   │
│   │   │   │   ├── graph.py
│   │   │   │   └── state.py
│   │   │   │
│   │   │   ├── mcp/
│   │   │   ├── rag/
│   │   │   ├── memory/
│   │   │   └── services/
│   │   │
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── migrations/
│   ├── tests/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── evaluation/
│   │   └── services/
│   │
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml
└── README.md
```

---

# 🐳 Running with Docker

ProcureOps can be run using Docker Compose.

### Prerequisites

- Docker
- Docker Compose

### Start the application

From the project root:

```bash
docker compose up --build
```

The main services are:

```text
Frontend  → http://localhost:5173
Backend   → http://localhost:8000
PostgreSQL → localhost:5432
Redis      → localhost:6379
```

### Stop the application

```bash
docker compose down
```

To remove persistent Docker volumes as well:

```bash
docker compose down -v
```

---

# ⚙️ Environment Variables

### Backend

Create:

```text
backend/.env
```

Example:

```env
HOST=0.0.0.0
DEBUG=false

DATABASE_URL=postgresql+psycopg://procureops:procureops_password@postgres:5432/procureops

REDIS_URL=redis://redis:6379/0

CORS_ORIGINS=http://localhost:5173

CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
```

---

### Frontend

Create:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

# 🗄️ Database

ProcureOps uses PostgreSQL for procurement and application data.

The application uses SQLAlchemy and Alembic for database management.

Run migrations:

```bash
docker compose exec backend alembic upgrade head
```

Check migration status:

```bash
docker compose exec backend alembic current
```

---

# 👤 Demo Accounts

The project includes demo users representing different procurement roles.

| Role | Example Account |
|---|---|
| Employee | `employee@procureops.example` |
| Procurement Analyst | `analyst@procureops.example` |
| Procurement Manager | `manager@procureops.example` |
| Procurement Head | `head@procureops.example` |
| Finance Officer | `finance@procureops.example` |
| Legal Officer | `legal@procureops.example` |
| Security Officer | `security@procureops.example` |
| Compliance Officer | `compliance@procureops.example` |
| CFO | `cfo@procureops.example` |
| Auditor | `auditor@procureops.example` |
| Administrator | `admin@procureops.example` |
| Vendor | `vendor@abc.com` |

> Demo credentials are intended for local development/testing only.

---

# 🔍 Health Check

Backend health endpoint:

```text
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

---

# 🔐 Security Considerations

The project demonstrates several security concepts relevant to AI applications:

- JWT-based authentication
- Role-based authorization
- Permission-based sensitive actions
- Active-user validation
- Resource validation
- Guardrails
- Prompt-injection protection
- Human approval for sensitive operations
- Environment-based secret management

The AI agent is not given unrestricted authority to execute sensitive procurement operations.

---

# 🎯 Design Principles

ProcureOps follows a few important design principles:

### 1. AI understands the request

The AI/agent layer handles natural-language interaction and determines the requested operation.

### 2. Business logic remains deterministic

Critical procurement operations are handled by application services rather than allowing the LLM to directly manipulate the database.

### 3. Sensitive actions require authorization

The agent cannot bypass permission checks.

### 4. Sensitive actions require human approval

Quotation approval and rejection are routed through HITL.

### 5. Current data comes from the application

Live procurement information is retrieved from PostgreSQL through application tools rather than relying on the LLM's knowledge.

### 6. Policies use RAG

Procurement policies and organizational knowledge are retrieved from the knowledge base before generating responses.

### 7. Agent execution is observable

LangSmith tracing is used to understand and debug the workflow.

---

# ⭐ Project Highlights

This project demonstrates practical implementation of:

```text
LLM Applications
       +
Agentic Workflows
       +
LangGraph
       +
MCP
       +
RAG
       +
Long-Term Memory
       +
Human-in-the-Loop
       +
RBAC
       +
Guardrails
       +
Evaluation
       +
Observability
       +
FastAPI
       +
React
       +
PostgreSQL
       +
Docker
```

The focus is on building an AI application where the LLM is responsible for understanding and orchestration while critical business operations remain controlled by deterministic backend services.

---

# 🚧 Future Improvements

Potential future enhancements include:

- More advanced policy-based authorization
- Additional procurement workflows
- More sophisticated memory retrieval
- Improved RAG evaluation
- More comprehensive agent evaluation datasets
- Streaming agent responses
- Background job processing
- Production deployment
- Advanced audit and compliance capabilities
- Improved frontend analytics

These are intentionally kept outside the current core implementation to keep the project focused and maintainable.

---

# 📌 Project Objective

The primary objective of ProcureOps is to demonstrate how modern AI engineering techniques can be combined with traditional backend engineering to build a practical enterprise-style AI assistant.

The project focuses on:

- Reliable agent orchestration
- Controlled tool usage
- Retrieval-grounded responses
- Persistent memory
- Secure execution of sensitive actions
- Human oversight
- Evaluation and observability

---

# 👨‍💻 Author

**Md Javed**

AI / ML Engineer | Python | FastAPI | LangGraph | RAG | Agentic AI
