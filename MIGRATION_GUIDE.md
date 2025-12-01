# Repository Migration Guide

## Overview

The **AI Photography Coach** project has been split into two separate repositories:

### 📍 **Original RAG Repository**
- **Name:** `ai-photography-coach-rag`
- **Purpose:** RAG-based document retrieval and photography knowledge base
- **Location:** `/Users/prasadt1/ai-photography-coach-rag`
- **Focus:** Vector embeddings, FAISS indexing, document retrieval

### 🤖 **New Agents Repository** 
- **Name:** `ai-photography-coach-agents`
- **Purpose:** Multi-agent system for personalized coaching
- **Location:** `/Users/prasadt1/ai-photography-coach-agents`
- **Focus:** Agent orchestration, LLM-based coaching, session management

---

## What Moved to New Repo

✅ **All Capstone Agent Files:**
- `agents_capstone/` – Complete agent system
  - `agents/` – VisionAgent, KnowledgeAgent, Orchestrator
  - `tools/` – ADK adapter, memory, context, EXIF, knowledge base
  - `notebooks/` – Demo notebook and scripts
  - `reports/` – Evaluation outputs
  - All documentation (WRITEUP.md, ADK_INTEGRATION.md, etc.)

✅ **Deployment & Evaluation:**
- `requirements.txt` – Dependencies
- `Dockerfile` – Container configuration
- `demo_eval.py` – Simple evaluation runner
- `run_evaluation.py` – Full-featured evaluation
- `SUBMISSION_README.md` – Quick start guide
- `DELIVERABLES.md` – Submission checklist

✅ **Documentation:**
- Comprehensive README with project overview
- .gitignore optimized for Python projects

---

## What Stays in Original RAG Repo

📚 **RAG Components:**
- Vector embeddings and FAISS indexing
- Document retrieval pipeline
- Knowledge base construction
- Original RAG-based coaching logic (if any)

---

## Using the New Agents Repository

### Clone (if hosted on GitHub)
```bash
git clone https://github.com/prasadt1/ai-photography-coach-agents.git
cd ai-photography-coach-agents
```

### Local Setup
```bash
cd /Users/prasadt1/ai-photography-coach-agents
export GOOGLE_API_KEY="your_key"
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m streamlit run agents_capstone/app_streamlit.py
```

### Run Evaluation
```bash
python3 demo_eval.py
```

---

## Repository Structure

```
ai-photography-coach-agents/
├── README.md                    # Project overview
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Dependencies
├── Dockerfile                   # Container
├── SUBMISSION_README.md         # Quick start
├── DELIVERABLES.md              # Checklist
├── demo_eval.py                 # Simple runner
├── run_evaluation.py            # Full runner
│
└── agents_capstone/
    ├── app_streamlit.py         # Web UI
    ├── evaluate.py              # Evaluation harness
    ├── logging_config.py        # Logging setup
    ├── agents/                  # Agent implementations
    ├── tools/                   # Support tools
    ├── notebooks/               # Demos
    ├── reports/                 # Outputs (generated)
    ├── WRITEUP.md               # Rubric mapping
    ├── ADK_INTEGRATION.md       # ADK guide
    ├── OBSERVABILITY.md         # Logging guide
    ├── DEMO_OUTLINE.md          # Demo script
    └── README.md                # Agent project docs
```

---

## Git History

The new repository starts fresh with an initial commit containing all capstone files:

```
dde10cd (HEAD -> master) Initial commit: AI Photography Coach - Multi-Agent System
```

To view the history of individual files from the original RAG repo, you can:
1. Check `/Users/prasadt1/ai-photography-coach-rag` for original commit history
2. Or use git reflog in the original repo

---

## Next Steps

### For the New Agents Repo:
1. ✅ Verify all files are present
2. ✅ Test the application locally
3. ✅ Run evaluation harness
4. ⬜ Upload to GitHub (optional)
5. ⬜ Document any cloud deployment

### For the Original RAG Repo:
1. Remove `agents_capstone/` folder (no longer needed)
2. Keep RAG components intact
3. Update documentation to reference new agents repo
4. Maintain as reference/backup

---

## Important Notes

⚠️ **Do NOT sync** the two repositories – they should remain independent

📌 **Dependencies are identical** – Both can use same Python environment

🔄 **If you need to sync changes:**
- Copy only specific files between repos
- Use git cherry-pick for individual commits
- Consider using git submodules if tight coupling needed

---

## Reference

| Component | Location |
|-----------|----------|
| Agents | `/Users/prasadt1/ai-photography-coach-agents/agents_capstone/agents/` |
| Tools | `/Users/prasadt1/ai-photography-coach-agents/agents_capstone/tools/` |
| Web UI | `/Users/prasadt1/ai-photography-coach-agents/agents_capstone/app_streamlit.py` |
| Evaluation | `/Users/prasadt1/ai-photography-coach-agents/demo_eval.py` |
| Docs | `/Users/prasadt1/ai-photography-coach-agents/agents_capstone/` |

---

## Support

For questions about:
- **Agents repo setup:** See `README.md` in new repo
- **Agent architecture:** See `agents_capstone/ADK_INTEGRATION.md`
- **Evaluation:** See `SUBMISSION_README.md` or `DELIVERABLES.md`
- **RAG components:** Refer to original `ai-photography-coach-rag` repo

---

**Migration completed:** December 1, 2025

Both repositories are now independent and ready for separate development.
