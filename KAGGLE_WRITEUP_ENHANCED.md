# AI Photography Coach – Multi-Platform Agent System

**📺 Demo Video:** [Watch on YouTube](https://youtu.be/U77vk71Hmzc)  
**🚀 Live Demo:** [ai-agentic-photography-coach.streamlit.app](https://ai-agentic-photography-coach.streamlit.app)  
**💻 GitHub Repository:** https://github.com/prasadt1/ai-photography-coach-agents/tree/capstone-submission

⚠️ **Note:** Requires free Google Gemini API key (30-second setup at https://aistudio.google.com/app/apikey)

---

## Problem Statement

Photography learners face a significant challenge: **getting personalized, actionable feedback on their work**. While online tutorials teach rules and techniques, beginners struggle to identify specific issues in their own photos and receive guidance tailored to their skill level and the actual image they captured.

Traditional solutions fall short:
- **Generic tutorials** don't address specific photos or situations
- **Photography forums** provide slow, inconsistent feedback
- **Paid coaches** are expensive and not scalable
- **Simple RAG systems** only retrieve static articles without contextual analysis

The problem is compounded when learners need multi-turn conversations—asking follow-up questions, clarifying advice, or discussing technical trade-offs. A single-shot answer isn't enough; they need an interactive coach that remembers context and adapts to their learning journey.

**Why this matters:** With millions of aspiring photographers worldwide and the democratization of high-quality cameras (including smartphones), there's enormous demand for scalable, intelligent coaching that can analyze actual images, understand conversation history, and provide personalized guidance at any skill level.

---

## Why Agents?

Photography coaching requires **specialized capabilities working together**: technical analysis (EXIF, exposure), visual composition (rule of thirds, balance), and contextual coaching (skill-adaptive feedback). 

**Agents solve this through:**
1. **Specialization** – VisionAgent (image analysis), ChatCoach (conversation), KnowledgeAgent (education)
2. **Multimodal processing** – Images + EXIF metadata + conversation text
3. **Stateful dialogue** – Orchestrator maintains session history for coherent multi-turn conversations
4. **Modularity** – Add new agents, test independently, deploy with ADK

**Why not RAG?** RAG retrieves documents but can't analyze images, track conversations, or coordinate specialized tasks.

---

## System Architecture

**Core Innovation:** A single, reusable agent implementation that deploys across **three platforms without code duplication**: ADK Runner (cloud), MCP Server (Claude Desktop), and Python API (custom apps).

### 1. Agent Coordination Pattern

![Agent Coordination Pattern](https://github.com/prasadt1/ai-photography-coach-agents/raw/capstone-submission/assets/diagrams/agent_coordination_pattern.png)

**Flow:** User Request → Orchestrator (parent agent) → VisionAgent analyzes photo (EXIF + composition) → KnowledgeAgent generates coaching (RAG + Gemini 2.5 Flash) → Orchestrator aggregates → Unified response with technical analysis, advice, and practice exercises.

The Orchestrator mediates **all** communication between sub-agents using the **Mediator Pattern** for loose coupling and testability.

### 2. Agent Hierarchy with Data Structures

![Agent Hierarchy Detailed](https://github.com/prasadt1/ai-photography-coach-agents/raw/capstone-submission/assets/diagrams/agent_hierarchy_detailed.png)

**Parent Agent: Orchestrator**
- Routes queries to specialized sub-agents
- Maintains conversation history across turns
- Implements context compaction for long sessions
- Persists state (SQLite with ADK adapter pattern)

**Sub-Agent 1: VisionAgent** (Gemini 2.5 Flash Vision)
- Extracts EXIF metadata (camera, ISO, aperture, shutter, focal length)
- Analyzes composition with Gemini Vision
- Detects issues with severity scoring (low/medium/high)
- Outputs structured `VisionAnalysis` dataclass

**Sub-Agent 2: KnowledgeAgent** (Gemini 2.5 Flash + RAG)
- Retrieves photography principles (Hybrid CASCADE RAG)
- Generates personalized coaching advice
- Adapts language to skill level
- Outputs structured `CoachingResponse` dataclass with citations

### 3. Multi-Platform Deployment

![Multi-Platform Architecture](https://github.com/prasadt1/ai-photography-coach-agents/raw/capstone-submission/assets/diagrams/multi_platform_architecture.png)

**Same agents, three deployment modes:**

| Platform | Use Case | Technology |
|----------|----------|------------|
| **ADK Runner** | Production cloud deployment | `google.adk` with LlmAgent, Runner, Sessions |
| **MCP Server** | Claude Desktop integration | JSON-RPC 2.0 over stdio |
| **Python API** | Custom applications | Direct imports, notebooks, scripts |

**Key Innovation:** Zero code duplication—the same `Orchestrator`, `VisionAgent`, and `KnowledgeAgent` work everywhere. Only the deployment wrapper changes.

### 4. Hybrid RAG CASCADE

![Hybrid RAG CASCADE](https://github.com/prasadt1/ai-photography-coach-agents/raw/capstone-submission/assets/diagrams/hybrid_rag_cascade.png)

**Three-tier retrieval:**
1. **Curated Knowledge** (20 principles) → NumPy similarity, <10ms
2. **FAISS Vector Store** (1000+ docs) → ~50ms latency
3. **Gemini Grounding** → Source attribution, ~200ms

Cascade logic: Try curated first → Fallback to FAISS → Always add grounding citations.

### 5. Session & Memory Management

SQLite backend with ADK adapter enables 50+ turn conversations. Recent 3 turns preserved at full fidelity, history summarized to prevent token overflow.

### 6. Evaluation Pipeline

![Evaluation Pipeline](https://github.com/prasadt1/ai-photography-coach-agents/raw/capstone-submission/diagrams_old_mermaid/evaluation_pipeline.png)

**LLM-as-Judge** scores 4 dimensions: Relevance, Completeness, Accuracy, Actionability (0-10 each). Outputs HTML dashboard + CSV + JSON.

---

## Demo

**🚀 Try it Live:** https://ai-agentic-photography-coach.streamlit.app

**Live Demo Flow:**

1. **Setup** → Paste your free API key from Google AI Studio in the sidebar
2. **Upload Photo** → Drag/drop a JPEG into the Streamlit interface
3. **Instant Analysis** → VisionAgent extracts EXIF (camera model, ISO 400, f/2.8, 1/500s, 85mm) and analyzes composition
4. **Ask Questions** → "How can I improve composition?" typed in chat
5. **Dynamic Coaching** → KnowledgeAgent (powered by Gemini 2.5 Flash) responds:
   - References the specific centered subject issue detected by VisionAgent
   - Cites photography principles from RAG CASCADE
   - Provides actionable next steps based on current skill level
6. **Follow-up** → "What about in low light?" continues the conversation
7. **Contextual Response** → System recalls previous discussion and ISO 400, adapting advice for low-light scenarios
8. **Observability** → Debug panel shows agent traces, latency (<3s), and session state

**Evaluation Results** (Automated LLM-as-Judge):
- **Overall Score:** 8.58/10
- **Response Quality:** 4.2/5
- **Citation Accuracy:** 95%+ responses grounded in RAG
- **Average Latency:** 26.6s (includes vision analysis + coaching + RAG)
- **EXIF Extraction:** 100% accuracy on test images

The system handles 50+ turn conversations, maintains context across sessions via SQLite, and provides production-grade observability with structured logging.

---

## The Build

### Architecture & Tools

**Multi-Agent System:**
- **Orchestrator** – Session management, agent coordination, context compaction
- **VisionAgent** – EXIF extraction, Gemini Vision analysis, composition issue detection
- **KnowledgeAgent** – Gemini 2.5 Flash-powered coaching with conversation history

**Technology Stack:**
- **Python 3.11.14** – Core language
- **Google Gemini 2.5 Flash** – LLM for coaching + vision analysis
- **text-embedding-004** – RAG embeddings (768 dimensions)
- **FAISS** – Vector similarity search (1000+ documents)
- **Streamlit 1.30** – Web UI framework
- **SQLite** – Session persistence (`agents_memory.db`)
- **Docker** – Production containerization
- **PIL/Pillow** – Image processing and EXIF extraction
- **google.adk 1.19.0** – Agent Development Kit integration

### 5-Day Build Process

**Day 1:** Multi-agent architecture with Orchestrator + ADK adapter pattern  
**Day 2:** VisionAgent (EXIF + Gemini Vision) + KnowledgeAgent (Gemini 2.5 Flash + Hybrid CASCADE RAG)  
**Day 3:** Structured logging, latency tracking, context compaction  
**Day 4:** LLM-as-Judge evaluation (4 dimensions, 8.58/10 score)  
**Day 5:** Multi-platform deployment (ADK Runner + MCP Server + Python API), Docker containerization

### Key Engineering Decisions

**Why multi-agent over monolithic LLM?**
- Specialized agents excel at specific tasks (vision analysis vs. coaching)
- Modular design enables independent testing and future enhancements
- Clean separation of concerns improves maintainability

**Why SQLite over in-memory only?**
- Persistent sessions survive app restarts
- Users can return to previous conversations
- Lightweight enough for local dev, scalable to cloud with ADK adapter

**Why LLM-as-Judge?**
- Automates quality assurance at scale
- Eliminates subjective human bias
- Provides quantitative metrics (0-10 scores) for iterative improvement

### Key Challenges

**Static Responses:** Rewrote KnowledgeAgent with full Gemini integration for dynamic coaching  
**Token Limits:** Context compaction enables 50+ turn conversations  
**Encoding:** UTF-8 + HTML escaping for clean reports

### Production-Ready Features

**Three Deployment Modes:** ADK Runner (`google.adk 1.19.0`), MCP Server (JSON-RPC 2.0, Claude Desktop ready), Python API  
**Scalability:** Thread-safe memory, Docker containerization, SQLite → Cloud SQL migration path  
**Observability:** Structured logging, latency tracking, debug panels

---

## Future Enhancements

**Additional Agents:** StyleAgent (artistic analysis), ComparisonAgent (portfolio review), TechnicalAgent (gear recommendations)  
**Cloud Scale:** Google Cloud Run deployment, horizontal scaling, authentication  
**Advanced Memory:** Long-term progress tracking, personalized learning paths, skill level detection  
**Tool Integration:** Lightroom presets, Photoshop actions, mobile app APIs  
**Community:** Batch portfolio review, peer comparison, daily challenges

---

---

## Quick Start

**Repository:** https://github.com/prasadt1/ai-photography-coach-agents.git

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your_gemini_api_key"

# Run 3-platform demonstration
python3 demo_3_platforms.py

# Or launch Streamlit web app
python3 -m streamlit run agents_capstone/app_streamlit.py

# Run automated evaluation
python3 demo_eval.py
```

**Get API Key:** https://aistudio.google.com/app/apikey (Free, 30 seconds)

---

## Testing & Verification

**All three platforms tested and verified functional:**

**Streamlit App** ✅ - Live at https://ai-agentic-photography-coach.streamlit.app with multi-agent orchestration, RAG citations, EXIF extraction, session management

**ADK Integration** ✅ - Transparent fallback to SQLite, compatible with `InMemorySessionService`, tested session storage and list operations

**MCP Server** ✅ - 3 tools registered (`analyze_photo`, `coach_on_photo`, `get_session_history`), JSON-RPC 2.0 compliant, Claude Desktop ready

**Evaluation Score:** 8.58/10 via LLM-as-Judge framework (4 dimensions: relevance, completeness, accuracy, actionability)

**Documentation:** Complete test logs in `DEPLOYMENT_VERIFICATION.md`, architecture in `ADK_INTEGRATION.md`, evaluation report in `agents_capstone/reports/`

---

## Key Takeaways

**What Makes This Special:**

1. **Multi-Platform Architecture** – Single agent codebase deploys to ADK (cloud), MCP (Claude Desktop), and Python API without code duplication
2. **Real ADK Integration** – Not just ADK-compatible, but actually using `google.adk 1.19.0` with LlmAgent, Runner, and Sessions
3. **Novel RAG Architecture** – Hybrid CASCADE combines curated precision with FAISS breadth and grounding trust
4. **Production-Grade** – Full observability, evaluation harness (8.58/10 score), Docker containerization, session persistence
5. **Truly Multi-Agent** – Not a wrapper around one LLM, but coordinated specialists (Vision + Knowledge + Orchestrator) with structured data contracts

**Impact:** Demonstrates how Google's agent technologies can solve real-world problems at scale, with architecture patterns applicable to any domain requiring specialized expertise, multimodal reasoning, and stateful conversations.
