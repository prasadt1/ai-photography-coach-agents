# AI Photography Coach – Capstone Rubric Writeup

This document maps the implemented AI Photography Coach capstone project to the Google AI Agents Intensive course rubric (Days 1–5).

---

## Executive Summary

The **AI Photography Coach** is an agentic system that:
1. Analyzes user photos using Gemini Vision (EXIF metadata + composition analysis).
2. Provides personalized coaching via a Knowledge Agent (multi-turn Q&A).
3. Manages session state and persistent memory using an ADK-compatible adapter.
4. Exposes observability (logs, traces, metrics) and evaluation harness.
5. Deploys locally via Streamlit and Docker (with optional Vertex AI extension).

**Repository:** `/Users/prasadt1/ai-photography-coach-rag/agents_capstone/`

---

## Rubric Mapping

### ✅ Day 1: Introduction to Agents

**Concept:** Multi-agent systems and agent design patterns.

**Implementation:**

| Feature | File(s) | Evidence |
|---------|---------|----------|
| **Multi-agent orchestration** | `agents/orchestrator.py` | Coordinates `VisionAgent` → `KnowledgeAgent` in a sequential pipeline. `run()` method demonstrates agent composition. |
| **Stateless agent functions** | `agents/vision_agent.py`, `agents/knowledge_agent.py` | Each agent is a pure function: `analyze(image, skill_level)` and `coach(query, analysis, session)`. No side effects within agents. |
| **Session state management** | `agents/__init__.py` (SESSION_STORE), `tools/adk_adapter.py` | In-memory `SESSION_STORE` dict + persistent backing. Session state tracks `skill_level`, `history`, conversation context. |
| **Agent interoperability** | `agents/orchestrator.py` | Agents communicate via typed dataclasses: `VisionAnalysis`, `CoachingResponse`. Clear contracts for agent inputs/outputs. |

**How to verify:**
```bash
cd agents_capstone
python3 -c "
from agents.orchestrator import Orchestrator
from agents.vision_agent import VisionAgent
from agents.knowledge_agent import KnowledgeAgent

v = VisionAgent()
k = KnowledgeAgent()
o = Orchestrator(v, k)
print('✓ Agents initialized and orchestrated')
"
```

---

### ✅ Day 2: Agent Tools & Interoperability with Model Context Protocol (MCP)

**Concept:** Custom tools, function calling, MCP integration.

**Implementation:**

| Feature | File(s) | Evidence |
|---------|---------|----------|
| **Custom tools** | `tools/exif_tool.py`, `tools/knowledge_base.py` | EXIF extraction tool parses camera metadata. Knowledge base tool retrieves photography principles (used by KnowledgeAgent). |
| **Tool definitions** | `tools/exif_tool.py` | Exposes `extract_exif()` function with typed inputs (image path) and outputs (dict of EXIF fields). |
| **MCP readiness** | `ADK_INTEGRATION.md` (Section: "Expand ADK Integration / Step 1") | Tool definitions and agent functions are structured to be wrapped as MCP server resources or ADK Tool objects. |
| **Long-running operations** | Session persistence with async context | Session state persists across calls; future MCP servers can checkpoint long-running analyses. |

**How to verify:**
```bash
cd agents_capstone
python3 -c "
from tools.exif_tool import extract_exif

# Test EXIF tool on any JPEG
exif = extract_exif('tmp_uploaded.jpg')
print('✓ EXIF tool works:', list(exif.keys()))
"
```

---

### ✅ Day 3: Context Engineering – Sessions & Memory

**Concept:** Stateful agents, session management, long-term memory.

**Implementation:**

| Feature | File(s) | Evidence |
|---------|---------|----------|
| **Session management** | `agents/__init__.py`, `agents/orchestrator.py` | `SESSION_STORE` dict keyed by `user_id`. Each session contains `skill_level`, `history[]` (chat turns), and metadata. |
| **In-session context** | `agents/knowledge_agent.py` | Agent reads full `session["history"]` and includes it in Gemini prompt for coherent multi-turn conversation. |
| **Long-term memory** | `tools/memory.py`, `tools/adk_adapter.py` | SQLite-backed key/value store (`agents_memory.db`). Orchestrator persists session after each run: `_persist_session()`. |
| **Context compaction** | `tools/context.py` | Heuristic summarizer: when history grows >6 turns, compacts into `session["compact_summary"]`. Stored in long-term memory. |
| **ADK SessionService** | `tools/adk_adapter.py` | Transparent adapter that detects ADK's `InMemorySessionService` and uses it if available; falls back to SQLite. Enables cloud-backed sessions. |

**How to verify:**
```bash
cd agents_capstone
python3 -c "
from tools import adk_adapter

adk_adapter.init()
# Test session persistence
adk_adapter.set_value('test_user', 'session', {'skill_level': 'intermediate'})
session = adk_adapter.get_value('test_user', 'session')
print('✓ Long-term memory works:', session)
"

# Check database file
ls -lh agents_memory.db
```

**UI Evidence:** Launch the app and note:
- Each user upload starts a new session (or loads prior session).
- Chat history persists across page refreshes.
- Debug panel shows persisted session keys and compact summary.

---

### ✅ Day 4: Agent Quality – Observability & Evaluation

**Concept:** Logs, traces, metrics; LLM-as-Judge evaluation; human-in-the-loop feedback.

**Implementation:**

| Feature | File(s) | Evidence |
|---------|---------|----------|
| **Structured logging** | `logging_config.py` | JSON log formatter with contextual fields (agent, user_id, latency, session_keys). Logs to stderr for Streamlit capture. |
| **Observability traces** | `app_streamlit.py` (debug panel) | Logs agent calls, LLM latency, EXIF extraction. Captured in `last_debug_logs` and displayed in UI. |
| **Metrics tracking** | `app_streamlit.py` (Observability panel) | UI panel shows: call count, avg latency, error count, last error. Metrics updated after each agent run. |
| **LLM-as-Judge evaluation** | `evaluate.py` | Scores responses on Relevance, Completeness, Accuracy, Actionability (1-10 scale). Uses Gemini to judge. |
| **Heuristic scoring** | `evaluate.py` | Local scoring: response length, presence of photography technical terms. Fallback when LLM judge unavailable. |
| **Evaluation reports** | `evaluate.py` (output: `reports/`) | Generates JSON (detailed logs), CSV (summary table), HTML (visual dashboard). Includes aggregates and per-prompt breakdowns. |

**How to verify:**
```bash
cd agents_capstone

# Run evaluation on a test image (if available)
python3 evaluate.py

# Check output
ls -lh reports/
cat reports/evaluation_summary.csv
open reports/evaluation_report.html  # or view in browser
```

**UI Evidence:**
- Upload an image and ask a question.
- Check the "Observability" panel (right side) for:
  - Agent latency
  - Session ID and compact summary
  - Error log (if any)
- Logs appear in terminal: `{"timestamp": "...", "level": "INFO", "agent": "VisionAgent", ...}`

---

### ✅ Day 5: Prototype to Production – Deployment & Scaling

**Concept:** Deployment, scalability, inter-agent communication (A2A Protocol), production readiness.

**Implementation:**

| Feature | File(s) | Evidence |
|---------|---------|----------|
| **Local deployment (Streamlit)** | `app_streamlit.py` | Runnable via `streamlit run agents_capstone/app_streamlit.py`. Serves web UI on `localhost:8501`. |
| **Docker deployment** | `Dockerfile`, `requirements.txt` | Containerized app with pinned dependencies. Can be deployed to Google Cloud Run, Heroku, or local Docker. |
| **Reproducible environment** | `requirements.txt` | All deps pinned (google-generativeai==0.8.0, streamlit==1.40.0, etc.). Ensures consistent runs across machines. |
| **Deployment script (optional)** | `scripts/docker_build_and_run.sh` (future) | To-do: provide shell script for one-command Docker build + run. |
| **A2A Protocol readiness** | `ADK_INTEGRATION.md` | Orchestrator can be extended to use ADK's A2A Protocol for inter-agent communication. Tools can be exposed as MCP servers. |
| **Vertex AI integration (optional)** | `ADK_INTEGRATION.md` (Step 4) | Documents how to deploy to Vertex AI Agent Engine with cloud-backed sessions. |
| **Scalability considerations** | `tools/adk_adapter.py`, `tools/memory.py` | SQLite can handle 100s of concurrent users; for production, use ADK's cloud-backed sessions or migrate to PostgreSQL/Firestore. |

**How to verify – Local Streamlit:**
```bash
cd /Users/prasadt1/ai-photography-coach-rag
export GOOGLE_API_KEY="YOUR_GEMINI_KEY"
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m streamlit run agents_capstone/app_streamlit.py
# Opens http://localhost:8501
```

**How to verify – Docker:**
```bash
cd /Users/prasadt1/ai-photography-coach-rag
docker build -t photo-coach:latest .
docker run -e GOOGLE_API_KEY="YOUR_GEMINI_KEY" -p 8501:8501 photo-coach:latest
# Opens http://localhost:8501
```

---

## Feature Matrix: Rubric Alignment

| Rubric Item | Status | Evidence File | Notes |
|---|---|---|---|
| **Day 1: Multi-agent design** | ✅ | `agents/orchestrator.py` | Vision + Knowledge agents, sequential orchestration |
| **Day 1: Agent interoperability** | ✅ | `agents/*.py` | Typed dataclass communication |
| **Day 2: Custom tools** | ✅ | `tools/exif_tool.py`, `knowledge_base.py` | EXIF extraction, principle retrieval |
| **Day 2: Tool definitions** | ✅ | `tools/exif_tool.py` | Structured input/output schemas |
| **Day 2: MCP / Long-running ops** | 🟡 | `ADK_INTEGRATION.md` | Framework in place; MCP server wrapping is optional extension |
| **Day 3: Session management** | ✅ | `agents/orchestrator.py`, `SESSION_STORE` | Per-user sessions with history |
| **Day 3: Long-term memory** | ✅ | `tools/memory.py`, `adk_adapter.py` | SQLite persistence + ADK adapter |
| **Day 3: Context compaction** | ✅ | `tools/context.py` | Summarizes long histories |
| **Day 4: Observability (logs)** | ✅ | `logging_config.py`, `app_streamlit.py` | JSON structured logs |
| **Day 4: Observability (traces)** | ✅ | `app_streamlit.py` (debug panel) | Agent call traces, latency |
| **Day 4: Observability (metrics)** | ✅ | `app_streamlit.py` (Observability panel) | Call count, latency, error tracking |
| **Day 4: LLM-as-Judge evaluation** | ✅ | `evaluate.py` | Scores relevance, completeness, accuracy |
| **Day 4: Evaluation reports** | ✅ | `evaluate.py` (output: JSON/CSV/HTML) | Comprehensive scoring dashboards |
| **Day 5: Local deployment** | ✅ | `app_streamlit.py` | Streamlit web app |
| **Day 5: Docker deployment** | ✅ | `Dockerfile`, `requirements.txt` | Container-ready |
| **Day 5: Reproducible environment** | ✅ | `requirements.txt` | Pinned versions |
| **Day 5: Scalability planning** | ✅ | `ADK_INTEGRATION.md` | Discusses migration to cloud sessions |
| **Day 5: A2A Protocol (optional)** | 🟡 | `ADK_INTEGRATION.md` | Framework in place; extension recommended |

---

## Key Accomplishments

1. **Multi-turn coaching experience:** Users upload a photo, see EXIF metadata and composition analysis, then ask follow-up questions. Chat context is maintained across turns and persisted.

2. **Gemini integration:** Both VisionAgent and KnowledgeAgent use Gemini 2.5 Flash for powerful image and text understanding. EXIF metadata enriches coaching accuracy.

3. **ADK-ready architecture:** Session storage and memory layer transparently support ADK's `InMemorySessionService` when available, enabling easy migration to cloud backends.

4. **Observability from day 1:** Structured logging, latency tracking, and error handling are built in. Debug panels in the UI provide visibility into agent decisions.

5. **Evaluation framework:** LLM-as-Judge scoring + local heuristics provide rigorous evaluation. Reports in JSON, CSV, and HTML formats for analysis.

6. **Deployment-ready:** Dockerfile and pinned requirements enable reproducible runs. Can be deployed to Google Cloud Run, Heroku, or Streamlit Cloud with minimal changes.

---

## How to Run the Full Demo

### Prerequisites
```bash
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
export PYTHONPATH=$PWD:$PYTHONPATH
cd /Users/prasadt1/ai-photography-coach-rag
```

### Option 1: Local Streamlit
```bash
python3 -m streamlit run agents_capstone/app_streamlit.py
# Open http://localhost:8501
```

### Option 2: Docker
```bash
docker build -t photo-coach:latest .
docker run -e GOOGLE_API_KEY="YOUR_KEY" -p 8501:8501 photo-coach:latest
# Open http://localhost:8501
```

### Run Evaluation
```bash
cd agents_capstone
python3 evaluate.py
# Check reports/ folder for JSON, CSV, HTML outputs
```

---

## Submission Artifacts

- **This WRITEUP.md** – maps all features to rubric
- **ADK_INTEGRATION.md** – explains ADK integration and course concepts
- **OBSERVABILITY.md** (to-do) – describes metrics collection and extension points
- **DEMO_OUTLINE.md** (to-do) – short walkthrough and optional video shots
- **Demo Notebook** (to-do) – Jupyter notebook showing end-to-end flow
- **Evaluation Report** – HTML/CSV summaries from `evaluate.py`
- **README.md** (updated) – setup and run instructions
- **Dockerfile** – reproducible container image

---

## Optional Extensions (Recommended)

1. **Expand ADK integration:** Formalize agents as ADK Tool objects (see `ADK_INTEGRATION.md`).
2. **MCP server:** Wrap agents as MCP resources for external tool orchestration.
3. **Vertex AI deployment:** Deploy to Agent Engine with cloud-backed sessions.
4. **A2A Protocol:** Enable inter-agent communication via ADK's protocol.
5. **Extended evaluation:** Add human-in-the-loop feedback loops; store scores in memory for continuous improvement.

---

**Project Status:** Ready for capstone submission with core rubric items (Days 1–4) fully implemented. Day 5 optional extensions (ADK tools, MCP, Vertex AI deployment) provided as documented roadmap.

**Built for:** Google AI Agents Intensive – Capstone Project
