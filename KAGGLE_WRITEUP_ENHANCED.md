# AI Photography Coach: Multi-Agent System with Gemini

**GitHub Repository:** https://github.com/prasadt1/ai-photography-coach-agents.git

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

**Agents are the right solution because this problem requires specialized capabilities that must work together:**

### 1. **Specialized Expertise**
Photography coaching demands distinct skills:
- **Technical analysis** (EXIF reading, exposure assessment)
- **Visual composition** (rule of thirds, leading lines, balance)
- **Contextual coaching** (adapting advice to skill level and conversation history)

A single monolithic LLM would struggle to excel at all three. Multiple specialized agents allow each to focus on what it does best.

### 2. **Multimodal Reasoning**
The system must process both:
- **Visual data** (the photo itself via Gemini Vision)
- **Metadata** (EXIF: ISO, aperture, shutter speed)
- **Conversation text** (user questions and history)

VisionAgent handles image+metadata analysis, while KnowledgeAgent focuses on natural language coaching—clean separation of concerns.

### 3. **Stateful Conversations**
Learners ask follow-up questions like "What about in low light?" after receiving composition advice. An Orchestrator agent maintains session state, tracks conversation history, and coordinates between specialists—enabling true multi-turn dialogue.

### 4. **Scalability & Modularity**
The multi-agent design allows:
- Adding new agents (e.g., StyleAgent for artistic advice) without rewriting existing code
- Independent testing and evaluation of each agent
- Future cloud deployment with Google's Agent Development Kit (ADK)

**Why not a simple RAG?** RAG retrieves documents but doesn't analyze images, track conversations, or coordinate specialized tasks. Agents provide the intelligence layer needed for interactive, context-aware coaching.

---

## What You Created

### Multi-Agent System Flow

![Multi-Agent System Flow](diagrams/multi_agent_flow.png)

Flow Order: 1 Upload → 2 Vision analysis → 3 Issues/EXIF returned → 4 Coaching request → 5 LLM prompt → 6 Gemini response → 7 KnowledgeAgent crafts coaching → 8 Response rendered and persisted.

**Components:**
1. **Orchestrator** – Session management, memory persistence, agent coordination
2. **VisionAgent** – EXIF extraction, Gemini Vision analysis, composition issue detection
3. **KnowledgeAgent** – Dynamic LLM-powered coaching using Gemini 1.5 Flash with conversation history
4. **Memory Layer** – SQLite-backed persistence with context compaction for long conversations

### Evaluation Pipeline

![Evaluation Pipeline](diagrams/evaluation_pipeline.png)

Scoring Dimensions: Relevance (focus), Completeness (coverage), Accuracy (technical correctness), Actionability (practical next steps). All scores (0–10) aggregated into summary + detailed artifacts.

Diagram Source: See `diagrams/*.mmd` for Mermaid definitions. Exported to PNG for reliable Kaggle rendering.

---

## Demo

**Live Demo Flow:**

1. **Upload Photo** → User drags/drops a JPEG into the Streamlit web interface
2. **Instant Analysis** → VisionAgent extracts EXIF (camera model, ISO 400, f/2.8, 1/500s, 85mm) and analyzes composition
3. **Ask Questions** → "How can I improve composition?" typed in chat
4. **Dynamic Coaching** → KnowledgeAgent (powered by Gemini 1.5 Flash) responds:
   - References the specific centered subject issue detected by VisionAgent
   - Suggests rule of thirds placement
   - Provides actionable next steps based on current skill level
5. **Follow-up** → "What about in low light?" continues the conversation
6. **Contextual Response** → System recalls previous discussion and ISO 400, adapting advice for low-light scenarios
7. **Observability** → Debug panel shows agent traces, latency (<3s), and session state

**Evaluation Results:**
- Relevance: 8.5/10
- Completeness: 8.2/10  
- Accuracy: 9.0/10
- Actionability: 8.7/10

The system handles 50+ turn conversations, maintains context across sessions via SQLite, and provides production-grade observability with structured logging.

---

## The Build

### Architecture & Tools

**Multi-Agent System:**
- **Orchestrator** – Session management, agent coordination, context compaction
- **VisionAgent** – EXIF extraction, Gemini Vision analysis, composition issue detection
- **KnowledgeAgent** – Gemini 1.5 Flash-powered coaching with conversation history

**Technology Stack:**
- **Python 3.11.14** – Core language
- **Google Gemini API** – gemini-1.5-flash-002 (text), gemini-1.5-flash-latest (vision)
- **Streamlit 1.30** – Web UI framework
- **SQLite** – Session persistence (`agents_memory.db`)
- **Docker** – Production containerization
- **PIL/Pillow** – Image processing and EXIF extraction

### 5-Day Build Process

**Day 1 – Foundation:**
- Multi-agent architecture with clean separation of concerns
- Orchestrator for session lifecycle management
- ADK-compatible adapter pattern for future cloud deployment

**Day 2 – Agent Implementation:**
- VisionAgent: EXIF extraction, Gemini Vision integration, issue detection (centered subjects, depth of field, exposure)
- KnowledgeAgent: **Full Gemini 1.5 Flash integration** (dynamic LLM responses, not templates), conversation history tracking (last 3 turns), photography knowledge base retrieval

**Day 3 – Observability:**
- Structured JSON logging with agent call traces
- Latency tracking for each operation
- Debug panel in Streamlit (session state, agent calls, performance metrics)
- Context compaction to prevent token overflow in long conversations

**Day 4 – Evaluation:**
- LLM-as-Judge framework with 4 dimensions: Relevance, Completeness, Accuracy, Actionability
- Gemini as automated evaluator (eliminates human bias)
- HTML dashboard + CSV export + JSON detailed results
- Three evaluation runners: `demo_eval.py`, `run_evaluation.py`, `quick_eval.py`

**Day 5 – Production Deployment:**
- Streamlit web app with file upload, real-time EXIF display, chat interface
- Docker containerization with pinned dependencies (`Dockerfile` + comprehensive `DEPLOYMENT.md` guide)
- SQLite persistence for session restoration across app restarts
- **ADK-ready architecture** with adapter pattern for seamless Google Cloud migration
- Deployment documentation for Cloud Run, Docker, and Agent Development Kit

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

### Challenges Overcome

**Challenge 1: Static Responses**
- Problem: Initial KnowledgeAgent used hardcoded templates
- Solution: Complete rewrite with Gemini 1.5 Flash integration, structured prompts including conversation history
- Result: Dynamic, context-aware coaching

**Challenge 2: Token Limits**
- Problem: Long conversations exceeded context windows
- Solution: Context compaction preserving last 3 turns + summarized history
- Result: Supports 50+ turn conversations

**Challenge 3: Encoding Issues**
- Problem: HTML reports displayed garbled characters
- Solution: UTF-8 charset + HTML entity escaping
- Result: Clean, professional reports

### Production-Ready Architecture

**Deployment Readiness:**
The system is architected for production deployment from day one:

**ADK Compatibility:**
- Memory adapter pattern (`tools/adk_adapter.py`) matches Google Agent Development Kit API
- Stateless agent design enables cloud scaling
- Easy migration path from SQLite → Cloud SQL/Firestore documented in `DEPLOYMENT.md`

**Comprehensive Documentation:**
- `DEPLOYMENT.md`: Complete guide for Docker, Cloud Run, and ADK deployment
- `VIDEO_SCRIPT.md`: YouTube demo script for showcasing the system
- Inline code comments explain design decisions and implementation details
- README with quick-start instructions and architecture overview

**Scalability Features:**
- Thread-safe memory layer for concurrent users
- Context compaction prevents token overflow in long sessions
- Structured logging for production observability
- Docker containerization with health checks and restart policies

**Cloud Deployment Path:**
The system can be deployed to Google Cloud Run in minutes:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-coach
gcloud run deploy --image gcr.io/PROJECT_ID/ai-coach --memory 2Gi
```

See `DEPLOYMENT.md` for complete deployment instructions including environment setup, monitoring, and security best practices.

---

## If I Had More Time, This Is What I'd Do

### 1. **Additional Specialized Agents**
- **StyleAgent** – Analyze artistic style (minimalist, dramatic, vintage) and suggest creative improvements
- **ComparisonAgent** – Compare before/after edits or analyze multiple photos from a portfolio
- **TechnicalAgent** – Deep dive into lens choice, sensor performance, and gear recommendations

### 2. **Cloud Deployment with ADK**
- Migrate to Google Cloud Run using Agent Development Kit
- Implement horizontal scaling for multiple concurrent users
- Add authentication and user account management
- Integrate with Cloud Storage for persistent photo storage

### 3. **Advanced Memory & Learning**
- **Long-term memory** – Track user's progress over weeks/months
- **Personalized learning paths** – Identify weak areas and generate targeted exercises
- **Skill level detection** – Automatically adjust coaching complexity based on user proficiency

### 4. **Integration with Photo Editing Tools**
- Export coaching suggestions to Lightroom presets
- Generate Photoshop action scripts for recommended adjustments
- API integration with mobile photography apps

### 5. **Enhanced Evaluation**
- **A/B testing framework** – Compare different coaching strategies
- **User satisfaction tracking** – Collect feedback on response quality
- **Benchmark against human coaches** – Validate accuracy with professional photographers

### 6. **Community Features**
- **Batch portfolio review** – Analyze 10-50 photos in one session
- **Peer comparison** – "Compare my landscape skills to similar photographers"
- **Challenge mode** – Daily photography exercises with automated feedback

---

**Repository:** https://github.com/prasadt1/ai-photography-coach-agents.git

**Quick Start:**
```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your_gemini_api_key"
python3 -m streamlit run agents_capstone/app_streamlit.py
python3 demo_eval.py  # Run evaluation
```

---

**Word Count:** 1,498 words
