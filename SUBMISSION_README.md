# AI Photography Coach – Capstone Submission

**Project Repository:** `/Users/prasadt1/ai-photography-coach-rag/agents_capstone/`

**Status:** ✅ Complete – Ready for submission

---

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/prasadt1/ai-photography-coach-rag
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
```

### 3. Run the App (Local Streamlit)

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m streamlit run agents_capstone/app_streamlit.py
```

Open `http://localhost:8501` in your browser.

### 4. Run Evaluation

```bash
# From project root (recommended):
export PYTHONPATH=$PWD:$PYTHONPATH
python3 run_evaluation.py

# Or from agents_capstone/:
cd agents_capstone
python3 quick_eval.py
```

Reports generated in `agents_capstone/reports/`:
- `evaluation_summary.csv` – Score table
- `evaluation_detailed.json` – Full results with scores
- `evaluation_report.html` – Visual dashboard

---

## Submission Contents

### Core Artifacts

| File | Purpose |
|------|---------|
| **WRITEUP.md** | ✅ Full rubric mapping (Days 1–5) with evidence |
| **ADK_INTEGRATION.md** | ✅ ADK setup, course concepts, extension guide |
| **OBSERVABILITY.md** | ✅ Logs, traces, metrics documentation |
| **DEMO_OUTLINE.md** | ✅ 5-min walkthrough + optional video shots |
| **capstone_demo.ipynb** | ✅ Interactive Jupyter notebook |
| **evaluate.py** | ✅ LLM-as-Judge evaluation harness |

### Source Code

| File | Purpose |
|------|---------|
| **agents/orchestrator.py** | Multi-agent orchestration + session management |
| **agents/vision_agent.py** | Gemini Vision + EXIF extraction |
| **agents/knowledge_agent.py** | Multi-turn coaching logic |
| **tools/adk_adapter.py** | ADK-ready session adapter |
| **tools/memory.py** | SQLite persistent storage |
| **tools/context.py** | Context compaction helper |
| **app_streamlit.py** | Web UI demo with observability |
| **logging_config.py** | Structured JSON logging |

### Deployment

| File | Purpose |
|------|---------|
| **Dockerfile** | Production container image |
| **requirements.txt** | Pinned dependencies |
| **scripts/docker_build_and_run.sh** | Docker smoke test script |

---

## Rubric Coverage

✅ **Day 1: Introduction to Agents**
- Multi-agent orchestration (Vision → Knowledge)
- Agent interoperability via typed dataclasses
- Session state management

✅ **Day 2: Agent Tools & Interoperability**
- Custom EXIF extraction tool
- Knowledge base tool
- MCP readiness (documented in ADK_INTEGRATION.md)

✅ **Day 3: Context Engineering – Sessions & Memory**
- Session management (in-memory + persistent)
- Multi-turn conversation history
- Context compaction for long histories
- ADK InMemorySessionService adapter

✅ **Day 4: Agent Quality**
- Structured JSON logging
- Observability panel (latency, metrics)
- LLM-as-Judge evaluation (relevance, completeness, accuracy, actionability)
- Evaluation reports (JSON, CSV, HTML)

✅ **Day 5: Prototype to Production**
- Local Streamlit deployment
- Docker containerization with pinned deps
- Reproducible environment
- ADK-ready for cloud deployment
- (Optional) A2A Protocol readiness

---

## Key Features

1. **Multi-Agent Orchestration**
   - VisionAgent analyzes photos (EXIF + composition)
   - KnowledgeAgent provides coaching (multi-turn Q&A)
   - Orchestrator manages state and persistence

2. **Gemini Integration**
   - Vision 2.5 Flash for image understanding
   - Text 2.5 Flash for conversational coaching
   - Real-time EXIF metadata extraction

3. **Session & Memory**
   - Per-user sessions with conversation history
   - SQLite-backed persistent memory
   - ADK adapter for transparent cloud-ready storage
   - Context compaction to keep prompts efficient

4. **Observability**
   - Structured JSON logs (agent, latency, errors)
   - Debug panel showing metrics and session state
   - Trace logs for each agent call

5. **Evaluation Framework**
   - LLM-as-Judge scoring (4 dimensions)
   - Local heuristics (length, technical terms)
   - Report generation (CSV, JSON, HTML)

6. **Production Ready**
   - Docker containerization
   - Error handling + fallbacks
   - Pinned dependencies
   - Extensible to ADK and cloud platforms

---

## How to Verify

### 1. Run Locally (5 minutes)

```bash
export GOOGLE_API_KEY="your_key"
export PYTHONPATH=$PWD:$PYTHONPATH
cd /Users/prasadt1/ai-photography-coach-rag

python3 -m streamlit run agents_capstone/app_streamlit.py
```

- Upload a photo
- Ask a question (e.g., "How can I improve composition?")
- Observe EXIF metadata and chat response
- Click "Debug & Observability" to see metrics

### 2. Run Evaluation

```bash
cd agents_capstone
python3 evaluate.py
```

- Produces `reports/evaluation_report.html` (open in browser)
- Shows LLM-as-Judge scores for sample prompts

### 3. Read Documentation

- **WRITEUP.md** – Detailed rubric mapping
- **ADK_INTEGRATION.md** – ADK and course concept alignment
- **OBSERVABILITY.md** – Logs and metrics guide
- **DEMO_OUTLINE.md** – Walkthrough and demo tips

### 4. Review Code

- `agents/` – Multi-agent architecture
- `tools/` – Session/memory/logging infrastructure
- `app_streamlit.py` – UI and state management

---

## Running via Docker

```bash
# Build image
docker build -t photo-coach:latest .

# Run with API key
docker run \
  -e GOOGLE_API_KEY="your_key" \
  -p 8501:8501 \
  photo-coach:latest

# Or use the test script (requires Docker + API key)
scripts/docker_build_and_run.sh
```

---

## Project Structure

```
agents_capstone/
├── app_streamlit.py              # Main UI + state management
├── evaluate.py                   # LLM-as-Judge evaluation
├── logging_config.py             # Structured logging setup
├── WRITEUP.md                    # ✅ Full rubric mapping
├── ADK_INTEGRATION.md            # ✅ ADK setup guide
├── OBSERVABILITY.md              # ✅ Logs/traces/metrics
├── DEMO_OUTLINE.md               # ✅ Demo walkthrough
│
├── agents/
│   ├── __init__.py               # Session store
│   ├── orchestrator.py           # Multi-agent orchestration
│   ├── vision_agent.py           # Gemini Vision + EXIF
│   ├── knowledge_agent.py        # Coaching logic
│   └── chat_coach.py             # Alias for KnowledgeAgent
│
├── tools/
│   ├── __init__.py
│   ├── adk_adapter.py            # ADK-ready session adapter
│   ├── memory.py                 # SQLite persistence
│   ├── context.py                # Context compaction
│   ├── exif_tool.py              # EXIF extraction
│   └── knowledge_base.py         # Photography principles KB
│
├── notebooks/
│   └── capstone_demo.ipynb       # Interactive demo notebook
│
├── reports/                      # Evaluation outputs (generated)
│   ├── evaluation_summary.csv
│   ├── evaluation_detailed.json
│   └── evaluation_report.html
│
└── Dockerfile                    # Production container

root/
├── requirements.txt              # Pinned dependencies
├── Dockerfile                    # Container config
└── scripts/
    └── docker_build_and_run.sh   # Docker smoke test
```

---

## Dependencies

Key packages (see `requirements.txt` for full list):
- `google-generativeai` – Gemini API
- `streamlit` – Web UI
- `pillow` – Image handling
- `sqlite3` – Built-in persistence

---

## Troubleshooting

### "No API_KEY or ADC found"
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

### "Module not found" errors
```bash
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Image upload fails
- Ensure image is JPEG or PNG
- File size < 20 MB
- Check `/tmp_uploaded.jpg` for saved image

### Chat response is empty
- Verify API key is valid
- Check app logs for "Gemini error"
- Use "Local FAQ Fallback" if external LLM fails

---

## Support & Questions

For issues or questions, refer to:
- **Code documentation** in docstrings
- **WRITEUP.md** for rubric mapping
- **ADK_INTEGRATION.md** for architecture
- **OBSERVABILITY.md** for debugging

---

## Submission Checklist

- ✅ Multi-agent system (Days 1–2)
- ✅ Session & memory management (Day 3)
- ✅ Observability & evaluation (Day 4)
- ✅ Deployment artifacts (Day 5)
- ✅ Runnable demo (Streamlit app)
- ✅ Documentation (WRITEUP, ADK guide, observability guide)
- ✅ Evaluation harness (LLM-as-Judge)
- ✅ Docker deployment ready
- ✅ Source code well-documented

---

**Built for:** Google AI Agents Intensive – Capstone Project

**Ready for submission:** Yes ✅
