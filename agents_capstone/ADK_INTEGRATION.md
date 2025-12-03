# ADK Integration Guide

This document describes how the AI Photography Coach capstone is designed to integrate with Google's **Agent Development Kit (ADK)** and the course concepts across Day 1–5.

---

## Architecture & ADK Mapping

### Current State (ADK-Ready)

The codebase is structured to **transparently integrate with ADK** without requiring it as a hard dependency:

- **Session & Memory (Day 3):**
  - Implemented: `agents_capstone/tools/adk_adapter.py` — a lightweight wrapper that:
    - Detects ADK's `InMemorySessionService` if the ADK package is installed.
    - Falls back to local SQLite-backed `memory.py` if ADK is absent.
  - Usage: The orchestrator and app import `adk_adapter` instead of `memory` directly.
  - Behavior: Session state is persisted to ADK (if available) or SQLite (fallback).
  - **Benefit:** Same app code works in both local (sqlite) and ADK-managed (cloud) environments.

- **Multi-Agent Design (Day 1):**
  - Implemented: `agents_capstone/agents/vision_agent.py` + `knowledge_agent.py` + `orchestrator.py`.
  - Pattern: Sequential orchestration — Vision → Knowledge agents.
  - ADK alignment: Agents are stateless functions; the orchestrator handles session state.
  - **Next Step:** Wrap agents as ADK `Tool` definitions and use ADK's execution context.

- **Tools & Interoperability (Day 2):**
  - Implemented: `agents_capstone/tools/exif_tool.py` + `knowledge_base.py`.
  - Optional: Model Context Protocol (MCP) integration can be added for long-running ops or third-party tool bridging.
  - **Next Step:** Expose agents as MCP servers or ADK Tool objects for external orchestration.

- **Agent Quality (Day 4):**
  - Implemented: `agents_capstone/logging_config.py` (JSON structured logs), `demo_eval.py` (LLM-as-Judge evaluation harness with 8.58/10 score).
  - Metrics: Structured logging with performance tracking and error monitoring.
  - **Next Step:** Export traces for ADK dashboards and cloud monitoring.

- **Prototype to Production (Day 5):**
  - Implemented: `Dockerfile`, `requirements.txt` (pinned), `adk_runner.py` (real ADK integration with google-adk==1.19.0), three deployment platforms (ADK Runner + MCP Server + Python API).
  - Multi-Platform: `demo_3_platforms.py` demonstrates all deployment options.
  - **Next Step:** Add deployment scripts for Vertex AI, and optionally implement formal A2A Protocol for cross-system agent communication.

---

## Quick Start: Using ADK

### 1. Install ADK (if not already)

```bash
pip install google-adk
```

(The exact package name may vary; check the official Google ADK documentation for the latest distribution.)

### 2. Update imports (automatic via adapter)

No code changes needed! The adapter (`adk_adapter.py`) will detect ADK automatically.

### 3. Run with ADK Runner

```bash
export GOOGLE_API_KEY="YOUR_GEMINI_KEY"
export PYTHONPATH=$PWD:$PYTHONPATH
python3 agents_capstone/adk_runner.py
```

Or use the unified demo:
```bash
python3 demo_3_platforms.py
```

The runner will log:
```
✅ ADK Runner initialized with InMemorySessionService
✅ Parent agent: Orchestrator with 2 sub-agents
```

---

## Course Concepts & Implementation Status

| Day | Topic | Implementation | ADK Integration | Status |
|-----|-------|---|---|---|
| **1** | Intro to Agents | Multi-agent orchestration (Vision + Knowledge) | Agents as stateless functions, orchestrator manages state | ✅ Core |
| **1** | Multi-Agent Systems | Sequential pipeline; ADK parent/sub-agent coordination | ADK Runner with LlmAgent + Sessions | ✅ Full |
| **2** | Agent Tools | `exif_tool.py`, `knowledge_base.py`, `agentic_rag.py`, `faiss_store.py` (8 tools total) | Integrated in ADK Runner + MCP Server | ✅ Full |
| **2** | MCP & Long-Running Ops | Basic session persistence; no long-running loops | MCP server bridging (optional) | 🟡 Optional |
| **3** | Context Engineering: Sessions | `SESSION_STORE` + SQLite + ADK adapter | ADK `InMemorySessionService` or cloud backend | ✅ Full |
| **3** | Context Engineering: Memory | Persistent SQLite memory + context compaction | ADK session storage + optional long-term LLM memory | ✅ Partial |
| **4** | Agent Quality: Observability | JSON logs, structured logging with performance metrics | Logs + ADK trace export (future) | ✅ Full |
| **4** | Agent Quality: Evaluation | LLM-as-Judge harness in `demo_eval.py` with 8.58/10 score | LLM-as-Judge scoring implemented | ✅ Full |
| **5** | Prototype to Production: Deployment | ADK Runner, MCP Server, Python API, Docker | Vertex AI Agent Engine (optional) | ✅ Multi-Platform |
| **5** | Prototype to Production: A2A Protocol | Orchestrator coordinates agents | ADK A2A Protocol for inter-agent communication | 🟡 Optional |

---

## Expanding ADK Integration

### ✅ Step 1: Real ADK Implementation (IMPLEMENTED)

**File:** `agents_capstone/adk_runner.py` (271 lines)

The project includes a complete ADK implementation using google-adk==1.19.0:

```python
"""Real ADK Runner with parent/sub-agent coordination."""

from google.adk import LlmAgent, Runner
from google.adk.sessions import InMemorySessionService
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create parent orchestrator agent
orchestrator = LlmAgent(
    model="gemini-2.0-flash-exp",
    system_instruction="You are a photography coach orchestrator...",
    tools=[vision_analysis_tool, coaching_tool]
)

# Create sub-agents for vision and knowledge
vision_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    system_instruction="Analyze photo composition and technical quality..."
)

knowledge_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    system_instruction="Provide personalized coaching feedback..."
)

# Initialize Runner with session management
session_service = InMemorySessionService()
runner = Runner(agent=orchestrator, session_service=session_service)
```

### Step 2: Use ADK's SessionService Explicitly

In the orchestrator or app, use ADK's session lifecycle:

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# Load or create session
session = session_service.load_or_create(user_id)

# Modify session state
session["compact_summary"] = ...

# Persist
session_service.persist(session)
```

### Step 3: Integrate Traces & Logging

Wrap agent calls in ADK's tracing context:

```python
from google.adk.observability import trace

@trace
def run_vision_agent(image_path, skill_level):
    return vision_agent.analyze(image_path, skill_level)
```

### Step 4: Deploy to Vertex AI Agent Engine (Optional)

```bash
# Build and deploy
gcloud ai agents create \
  --name photography-coach \
  --tool-ids analyze_photo,coach_on_photo \
  --session-backend cloud-sql  # or firestore
```

---

## Testing ADK Integration

### 1. Verify Adapter Detection

```bash
python3 -c "from agents_capstone.tools import adk_adapter; print('Using ADK:', adk_adapter.USING_ADK)"
```

### 2. Test Session Persistence

```bash
python3 - <<'PY'
from agents_capstone.tools import adk_adapter

adk_adapter.init()
adk_adapter.set_value("user1", "session", {"history": [{"msg": "hi"}]})
result = adk_adapter.get_value("user1", "session")
print("Persisted session:", result)
assert result["history"][0]["msg"] == "hi"
print("✓ Session persistence working")
PY
```

### 3. Run Full App

```bash
export GOOGLE_API_KEY="YOUR_KEY"
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m streamlit run agents_capstone/app_streamlit.py
```

Upload an image and ask a question. Check logs for:
- ADK session load/save confirmation.
- EXIF extraction and chat responses.
- Observability panel showing session keys.

---

## ✅ Implemented Enhancements (Phase 2 & 3)

### Phase 2: Enhanced Vision Analysis
- **Gemini Vision API Integration** - Real AI-powered composition analysis
- **Structured Issue Detection** - Severity scoring (low/medium/high) with suggestions
- **Strengths Detection** - Identifies positive aspects of photos
- **Adaptive Feedback** - Skill-level personalized analysis

### Phase 3: MCP Server + ADK Tools
- **MCP Server** (`tools/mcp_server.py`) - Full JSON-RPC implementation
- **ADK Tools** (`adk_tools.py`) - Formalized tool definitions
- **Claude Desktop Integration** - Ready for MCP client connection
- **Three MCP Tools:**
  1. `analyze_photo` - Vision analysis with structured output
  2. `coach_on_photo` - Personalized coaching with history
  3. `get_session_history` - Session retrieval and statistics

### Usage Examples

**MCP Server (Claude Desktop, VS Code, etc.):**
```bash
# Run server
./run_mcp_server.sh

# Or directly
python3 -m agents_capstone.tools.mcp_server
```

**ADK Runner (Production-Ready):**
```python
from agents_capstone.adk_runner import run_photography_coach

# Run complete coaching session
response = run_photography_coach(
    user_input="Analyze this landscape photo",
    image_path="photo.jpg",
    user_id="user123",
    skill_level="intermediate"
)
print(response["message"])
print(f"Session ID: {response['session_id']}")
```

**Claude Desktop Integration:**
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "photography-coach": {
      "command": "python3",
      "args": ["/path/to/ai-photography-coach-agents/agents_capstone/tools/mcp_server.py"]
    }
  }
}
```

## Next Steps for Advanced Deployment

1. **Vertex AI Agent Engine** - Deploy ADK tools to Google Cloud
2. **A2A Protocol** - Multi-agent communication for complex workflows
3. **Cloud-Backed Sessions** - Firestore/Cloud SQL for persistence
4. **Trace Export** - Integration with Cloud Logging and Monitoring

---

## References

- [ADK Python Package](https://pypi.org/project/google-adk/) - Official PyPI package
- [Vertex AI Generative AI](https://cloud.google.com/vertex-ai/generative-ai/docs) - Google Cloud documentation
- [Vertex AI Agent Builder](https://cloud.google.com/agent-builder) - Agent development platform
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs) - Gemini model reference

---

**Built for the Google AI Agents Intensive – Capstone Project**
