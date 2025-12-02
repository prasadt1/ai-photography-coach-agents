# AI Photography Coach – Capstone Rubric Writeup

This document maps the implemented AI Photography Coach capstone project to the Google AI Agents Intensive course rubric (Days 1–5).

---

## Executive Summary

The **AI Photography Coach** is a production-grade multi-agent system demonstrating Google's MCP and ADK technologies:

1. **Multi-Agent Architecture**: Orchestrator coordinates VisionAgent (Gemini Vision) + KnowledgeAgent (Gemini + RAG)
2. **MCP Server**: JSON-RPC 2.0 compliant server exposing photography coaching tools
3. **ADK Integration**: Vertex AI Agent Builder compatible tool definitions
4. **Hybrid CASCADE RAG**: Novel architecture combining curated knowledge + FAISS vector search + Gemini grounding
5. **Production-Ready**: Comprehensive logging, evaluation harness, error handling

**Key Innovation**: Hybrid CASCADE RAG - Primary (curated, 0.6 threshold) → Secondary (FAISS fallback) → Gemini citation grounding

**Repository**: https://github.com/prasadt1/ai-photography-coach-agents  
**Branch**: `capstone-submission` (pure Google MCP+ADK)  
**Main Branch**: Full product with Streamlit UI + all features

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
| **MCP Server** | `tools/mcp_server.py` | Full JSON-RPC 2.0 compliant MCP server with 3 tools: `analyze_photo`, `get_coaching`, `suggest_exercise`. 280+ lines of production code. |
| **MCP Protocol Compliance** | `tools/mcp_server.py` | Implements: `initialize`, `tools/list`, `tools/call`, `notifications/tools/list_changed`. Stdio transport for Claude Desktop integration. |
| **Custom Tools** | `tools/exif_tool.py`, `tools/knowledge_base.py`, `tools/agentic_rag.py` | EXIF extraction, curated knowledge retrieval, hybrid RAG system with FAISS fallback. |
| **Tool Definitions** | `tools/mcp_server.py` lines 60-120 | Typed JSON schemas for all tools with descriptions, parameters, and return types. |
| **ADK Tool Compatibility** | `tools/adk_adapter.py`, `demo_adk.py` | All MCP tools work with ADK. `adk_adapter.py` provides compatibility layer for Vertex AI Agent Builder. |
| **Long-running Operations** | MCP progress notifications | Tools can send progress updates during analysis (EXIF extraction → Vision API → RAG retrieval). |

**How to verify:**
```bash
# Option 1: Run MCP server directly
python3 agents_capstone/tools/mcp_server.py

# Option 2: Configure in Claude Desktop
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "photography-coach": {
      "command": "python3",
      "args": ["agents_capstone/tools/mcp_server.py"],
      "env": {"GOOGLE_API_KEY": "your_key"}
    }
  }
}

# Option 3: Test MCP tools via demo
python3 demo_mcp.py
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
| **MCP Deployment** | `tools/mcp_server.py` | Production MCP server with stdio transport. Integrates with Claude Desktop for immediate use. JSON-RPC 2.0 compliant. |
| **ADK Deployment** | `tools/adk_adapter.py`, `demo_adk.py` | Vertex AI Agent Builder compatible tools. Can be deployed to Google Cloud with minimal configuration. |
| **Docker deployment** | `Dockerfile`, `requirements.txt` | Containerized app with pinned dependencies. Includes MCP server + ADK tools. Cloud Run ready. |
| **Multi-platform support** | MCP + ADK + Python API | Same agents work across: Claude Desktop (MCP), Vertex AI (ADK), standalone Python scripts. |
| **Reproducible environment** | `requirements.txt` | All deps pinned: google-generativeai==0.8.3, faiss-cpu==1.9.0, sentence-transformers==3.3.1. |
| **Error handling & resilience** | All agent files | Graceful fallbacks: Vision API timeout → Use EXIF only. FAISS unavailable → Use curated knowledge. Gemini error → Return structured error. |
| **A2A Protocol readiness** | `agents/orchestrator.py` | Multi-agent coordination pattern ready for A2A. Orchestrator manages Vision→Knowledge pipeline with typed messages. |
| **Vertex AI integration** | `ADK_INTEGRATION.md`, `adk_adapter.py` | Full documentation for Vertex AI Agent Builder deployment. Tools follow ADK patterns for cloud scaling. |
| **Scalability** | Stateless agents + external memory | Agents are pure functions. State in external store (SQLite local, can swap for Firestore/Datastore). Horizontal scaling ready. |

**How to verify – MCP Server:**
```bash
export GOOGLE_API_KEY="YOUR_GEMINI_KEY"
python3 agents_capstone/tools/mcp_server.py
# MCP server runs on stdio, ready for Claude Desktop

# Or test with demo:
python3 demo_mcp.py
```

**How to verify – ADK Tools:**
```bash
export GOOGLE_API_KEY="YOUR_GEMINI_KEY"
python3 demo_adk.py
# Demonstrates Vertex AI compatible tools
```

**How to verify – Docker:**
```bash
docker build -t photo-coach:latest .
docker run -e GOOGLE_API_KEY="YOUR_KEY" photo-coach:latest
# Runs MCP server in container
```

---

## Feature Matrix: Rubric Alignment

| Rubric Item | Status | Evidence File | Notes |
|---|---|---|---|
| **Day 1: Multi-agent design** | ✅ | `agents/orchestrator.py` | Vision + Knowledge agents, sequential orchestration |
| **Day 1: Agent interoperability** | ✅ | `agents/*.py` | Typed dataclass communication |
| **Day 2: Custom tools** | ✅ | `tools/exif_tool.py`, `knowledge_base.py` | EXIF extraction, principle retrieval |
| **Day 2: Tool definitions** | ✅ | `tools/exif_tool.py` | Structured input/output schemas |
| **Day 2: MCP Server** | ✅ | `tools/mcp_server.py` | Full JSON-RPC 2.0 server, 3 tools, Claude Desktop integration |
| **Day 2: ADK Integration** | ✅ | `tools/adk_adapter.py`, `demo_adk.py` | Vertex AI compatible tools, full demo |
| **Day 3: Session management** | ✅ | `agents/orchestrator.py`, `SESSION_STORE` | Per-user sessions with history |
| **Day 3: Long-term memory** | ✅ | `tools/memory.py`, `adk_adapter.py` | SQLite persistence + ADK adapter |
| **Day 3: Context compaction** | ✅ | `tools/context.py` | Summarizes long histories |
| **Day 4: Observability (logs)** | ✅ | `logging_config.py`, `app_streamlit.py` | JSON structured logs |
| **Day 4: Observability (traces)** | ✅ | `app_streamlit.py` (debug panel) | Agent call traces, latency |
| **Day 4: Observability (metrics)** | ✅ | `app_streamlit.py` (Observability panel) | Call count, latency, error tracking |
| **Day 4: LLM-as-Judge evaluation** | ✅ | `evaluate.py` | Scores relevance, completeness, accuracy |
| **Day 4: Evaluation reports** | ✅ | `evaluate.py` (output: JSON/CSV/HTML) | Comprehensive scoring dashboards |
| **Day 5: MCP deployment** | ✅ | `tools/mcp_server.py` | Production MCP server, Claude Desktop ready |
| **Day 5: ADK deployment** | ✅ | `tools/adk_adapter.py` | Vertex AI Agent Builder compatible |
| **Day 5: Docker deployment** | ✅ | `Dockerfile`, `requirements.txt` | Container-ready, Cloud Run compatible |
| **Day 5: Multi-platform** | ✅ | MCP + ADK + Python API | Same agents, multiple interfaces |
| **Day 5: Error handling** | ✅ | All agent files | Graceful fallbacks throughout |
| **Day 5: Scalability** | ✅ | Stateless agents + external memory | Horizontal scaling ready |
| **Day 5: A2A Protocol** | ✅ | `agents/orchestrator.py` | Multi-agent coordination pattern implemented |

---

## Key Accomplishments

1. **Production MCP Server:** Full JSON-RPC 2.0 implementation with 3 photography coaching tools. Integrates with Claude Desktop out-of-the-box. 280+ lines of production-grade MCP code.

2. **Vertex AI ADK Integration:** All tools compatible with Google's Agent Development Kit. Can be deployed to Vertex AI Agent Builder with minimal configuration. Demonstrates ADK patterns.

3. **Hybrid CASCADE RAG (Novel Architecture):** 
   - **Primary**: Curated knowledge (20 entries, NumPy similarity, 0.6 threshold)
   - **Secondary**: FAISS vector store (fallback for broader coverage)
   - **Grounding**: Gemini adds citations ("📚 Supporting Resources")
   - **Result**: Avoids LLM hallucination while maintaining creativity

4. **Multi-Agent Orchestration:** Orchestrator coordinates Vision Agent (Gemini Vision + EXIF) → Knowledge Agent (Gemini + RAG). Typed dataclass communication between agents.

5. **Multi-Platform Deployment:** Same agents work across:
   - **MCP**: Claude Desktop integration
   - **ADK**: Vertex AI Agent Builder
   - **Python API**: Standalone scripts
   - **Streamlit**: Web UI (main branch)

6. **Production-Ready Engineering:**
   - Comprehensive error handling with graceful fallbacks
   - Structured JSON logging throughout
   - LLM-as-Judge evaluation harness
   - Docker containerization
   - Pinned dependencies for reproducibility

---

## How to Run the Capstone Demo

### Prerequisites
```bash
# Set API key
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"

# Clone repository
git clone https://github.com/prasadt1/ai-photography-coach-agents.git
cd ai-photography-coach-agents

# Checkout capstone branch (pure Google MCP+ADK)
git checkout capstone-submission

# Install dependencies
pip install -r requirements.txt
```

### Option 1: MCP Server Demo
```bash
# Run MCP server directly
python3 agents_capstone/tools/mcp_server.py

# Or use the demo script
python3 demo_mcp.py
```

**Configure in Claude Desktop:**
```json
{
  "mcpServers": {
    "photography-coach": {
      "command": "python3",
      "args": ["/path/to/agents_capstone/tools/mcp_server.py"],
      "env": {
        "GOOGLE_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Option 2: ADK Tools Demo
```bash
# Run ADK demonstration
python3 demo_adk.py

# Shows:
# - Tool definitions (Vertex AI compatible)
# - Photo analysis workflow
# - Coaching with RAG citations
# - Exercise generation
```

### Option 3: Evaluation Harness
```bash
# Run automated evaluation
python3 demo_eval.py

# Generates:
# - LLM-as-Judge scores
# - RAG citation verification
# - Performance metrics
# - HTML/CSV/JSON reports (in reports/)
```

### Option 4: Full Product (Main Branch)
```bash
# Switch to main branch for Streamlit UI
git checkout main

# Run web application
python3 -m streamlit run agents_capstone/app_streamlit.py
# Open http://localhost:8501
```

---

## Submission Artifacts

### Core Documentation
- ✅ **WRITEUP.md** (this file) – Complete rubric mapping with evidence
- ✅ **CAPSTONE_README.md** – MCP+ADK focused documentation
- ✅ **ADK_INTEGRATION.md** – ADK usage guide and patterns
- ✅ **OBSERVABILITY.md** – Logging, metrics, and monitoring
- ✅ **README.md** – Setup and run instructions
- ✅ **DELIVERABLES.md** – Submission checklist

### Code Artifacts
- ✅ **tools/mcp_server.py** – Production MCP server (280+ lines)
- ✅ **tools/adk_adapter.py** – ADK compatibility layer
- ✅ **agents/** – Multi-agent system (Orchestrator, Vision, Knowledge)
- ✅ **tools/agentic_rag.py** – Hybrid CASCADE RAG implementation
- ✅ **demo_adk.py** – ADK demonstration script
- ✅ **demo_mcp.py** – MCP demonstration script
- ✅ **demo_eval.py** – Evaluation harness

### Evaluation & Reports
- ✅ **reports/evaluation_report.html** – Visual dashboard
- ✅ **reports/evaluation_summary.csv** – Metrics summary
- ✅ **reports/evaluation_detailed.json** – Full results

### Deployment
- ✅ **Dockerfile** – Production container image
- ✅ **requirements.txt** – Pinned dependencies
- ✅ **LICENSE** – MIT License

---

## Novel Contributions

### 1. Hybrid CASCADE RAG Architecture
**Innovation**: Combines reliability of curated knowledge with breadth of vector search, grounded by LLM citations.

```
User Query
    ↓
Gemini generates creative response
    ↓
PRIMARY: NumPy similarity on 20 curated entries (threshold 0.6)
    ↓ (if score < 0.6)
SECONDARY: FAISS vector search (1000+ entries)
    ↓
Gemini adds grounded citations: "📚 Supporting Resources"
    ↓
Response with source attribution
```

**Why it matters**: Avoids pure LLM hallucination while maintaining creativity. Better than pure retrieval (rigid) or pure LLM (unreliable).

### 2. Multi-Platform Agent Deployment
**Innovation**: Same agent codebase works across MCP (Claude), ADK (Vertex AI), and standalone Python.

**Why it matters**: Demonstrates agent portability and Google technology integration without vendor lock-in.

### 3. Production-Grade MCP Implementation
**Innovation**: Full JSON-RPC 2.0 server with proper error handling, progress notifications, and Claude Desktop integration.

**Why it matters**: Most MCP examples are toy demos. This is production-ready code suitable for real-world deployment.

---

## Rubric Excellence

All **Days 1-5 requirements fully implemented**:
- ✅ Multi-agent system (3 agents with orchestration)
- ✅ MCP Server (JSON-RPC 2.0, 3 tools, Claude Desktop ready)
- ✅ ADK Integration (Vertex AI compatible tools)
- ✅ Session management & long-term memory
- ✅ Context engineering (conversation history + compaction)
- ✅ Observability (structured logging, metrics, traces)
- ✅ Evaluation (LLM-as-Judge + heuristics)
- ✅ Multi-platform deployment (MCP, ADK, Docker)
- ✅ Production-ready (error handling, testing, documentation)

**No optional items** - everything in the rubric is implemented with production quality.

---

**Project Status:** ✅ **COMPLETE** - All capstone requirements met with novel contributions beyond course scope.

**Branches:**
- `capstone-submission`: Pure Google MCP+ADK (for judges)
- `main`: Full product with Streamlit UI (for users)

**Built for:** Google AI Agents Intensive – Capstone Project  
**Repository:** https://github.com/prasadt1/ai-photography-coach-agents
