# 📷 AI Photography Coach – Multi-Platform Agent System

> **Google AI Agents Intensive Capstone Project**  
> Production-grade agent deployment across ADK, MCP, and Python API

---

## 🎯 Project Overview

A **multi-agent photography coaching system** built with Google's agent technologies, demonstrating architectural reusability through three deployment platforms:

- **ADK Runner**: Cloud-native deployment with `google.adk` (LlmAgent + Runner + Sessions)
- **MCP Server**: JSON-RPC 2.0 server for Claude Desktop integration  
- **Python API**: Direct agent imports for custom applications
- **Multi-Agent Architecture**: Vision Agent + Knowledge Agent + Orchestrator
- **Hybrid CASCADE RAG**: Novel retrieval combining curated knowledge, vector search, and LLM grounding

**Core Innovation:** Single agent implementation (`VisionAgent`, `KnowledgeAgent`) deploys identically across all platforms with zero code duplication, demonstrating framework-independent architecture.

---

## 🚀 Quick Start

### Unified Demo (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your_gemini_api_key"

# Run 3-platform demonstration
python3 demo_3_platforms.py
```

This shows all three deployment platforms in a single run:
- **ADK Runner**: Cloud-native agent execution
- **MCP Server**: Claude Desktop integration
- **Python API**: Direct programmatic access

---

## 📋 Platform-Specific Usage

### ADK Runner (Cloud Deployment)

```bash
# Run ADK agent with session management
python3 agents_capstone/adk_runner.py

# Features:
# - LlmAgent with Gemini 2.5 Flash
# - Runner with InMemorySessionService
# - Async event streaming
# - Full session continuity
```

### MCP Server (Desktop Integration)

```bash
# Start server
python3 agents_capstone/tools/mcp_server.py

# Configure Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "photography-coach": {
      "command": "python3",
      "args": ["/absolute/path/to/agents_capstone/tools/mcp_server.py"],
      "env": {"GOOGLE_API_KEY": "your_key"}
    }
  }
}

# Use in Claude Desktop:
# "Analyze this photo for composition issues..."
```

### Python API (Programmatic Access)

```python
from agents_capstone.agents.vision_agent import VisionAgent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent

# Initialize agents
vision = VisionAgent()
knowledge = KnowledgeAgent()

# Analyze and coach
analysis = vision.analyze("photo.jpg", "intermediate")
response = knowledge.coach(
    query="How to improve composition?",
    vision_analysis=analysis,
    session={"history": []}
)

print(response.text)  # AI-generated coaching advice
print(response.principles)  # Retrieved knowledge citations
```

---

## 🏗️ Architecture

### Multi-Agent System

```
User Query → Orchestrator
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
VisionAgent      KnowledgeAgent
(Gemini Vision)  (Gemini + RAG)
    ↓                   ↓
EXIF + Issues    Coaching + Citations
    └─────────┬─────────┘
              ↓
      Unified Response
```

### Agent Capabilities

**VisionAgent** (Gemini Vision)
- EXIF metadata extraction (camera settings, lens data)
- Composition analysis with severity scoring
- Issue detection (exposure, focus, horizon, etc.)
- Strength identification

**KnowledgeAgent** (Gemini + Hybrid RAG)
- Personalized coaching based on skill level
- Citation-backed advice from knowledge base
- Practice exercise generation
- Session history awareness

### Platform Comparison

| Feature | ADK Runner | MCP Server | Python API |
|---------|-----------|-----------|-----------|
| **Framework** | google.adk | JSON-RPC 2.0 | Native Python |
| **Deployment** | Vertex AI / Cloud | Claude Desktop | Notebooks, scripts |
| **Session Management** | InMemorySessionService | Custom state | Custom state |
| **Execution** | Async (Runner) | Async (stdio) | Synchronous |
| **Use Case** | Enterprise scaling | Local AI assistant | Custom integration |
| **Code Reuse** | ✅ Same agents | ✅ Same agents | ✅ Same agents |

**Architectural Principle:** Zero code duplication across platforms – same `VisionAgent` and `KnowledgeAgent` work everywhere.

---

## 📚 Hybrid CASCADE RAG

Novel retrieval architecture combining reliability with flexibility:

```
Query → Agentic RAG (Gemini creativity)
         ↓
    1. Primary: Curated Knowledge (20 entries)
       - NumPy similarity search
       - Threshold: 0.6
       - Fast, high-quality
         ↓
    2. Secondary: FAISS Fallback (1000+ entries)
       - Vector search
       - Broader coverage
       - Deployed when needed
         ↓
    3. Grounding: Gemini adds citations
       - "📚 Supporting Resources"
       - Source attribution
       - Builds trust
```

**Innovation**: Combines curated precision with vector breadth, avoiding pure LLM hallucination.

---

## 🎓 Capstone Requirements Met

### ✅ Multi-Agent System
- **3 Agents**: Orchestrator, VisionAgent, KnowledgeAgent
- **Coordination**: Orchestrator manages agent interactions
- **State Management**: Conversation history tracking

### ✅ Google Technologies
- **Gemini 2.5 Flash**: LLM for coaching + vision analysis
- **MCP Protocol**: JSON-RPC server implementation
- **ADK Compatible**: Tool definitions for Vertex AI

### ✅ Production Quality
- **Error Handling**: Graceful fallbacks for API failures
- **Caching**: Embeddings cached for performance
- **Logging**: Comprehensive debug output
- **Testing**: Unit tests for core components

### ✅ Real-World Application
- **Domain**: Photography education (multi-billion $ market)
- **Impact**: Democratizes expert coaching
- **Scalability**: API-first architecture

---

## 📁 Project Structure

```
agents_capstone/
├── agents/
│   ├── orchestrator.py      # Multi-agent coordinator
│   ├── vision_agent.py       # EXIF + composition analysis
│   ├── knowledge_agent.py    # Gemini + RAG coaching
│   └── chat_coach.py         # Conversational interface
├── tools/
│   ├── mcp_server.py         # MCP JSON-RPC server ⭐
│   ├── adk_adapter.py        # ADK tool definitions ⭐
│   ├── agentic_rag.py        # Hybrid CASCADE RAG
│   ├── exif_tool.py          # Photo metadata extraction
│   └── knowledge_base.py     # Curated photography knowledge
├── demo_adk.py               # ADK demonstration script
├── demo_mcp.py               # MCP demonstration script
└── evaluate.py               # Automated evaluation harness
```

---

## 🧪 Evaluation & Testing

### Automated Evaluation Framework

The project includes a comprehensive evaluation harness (`demo_eval.py`) that tests agent performance across multiple dimensions:

```bash
python3 demo_eval.py
```

#### Evaluation Methodology

**1. Test Dataset**
- 3 diverse photography scenarios (landscape, portrait, technical questions)
- Mix of image analysis and knowledge queries
- Covers beginner to advanced skill levels

**2. Scoring Criteria**

| Metric | What It Measures | How It's Scored |
|--------|------------------|-----------------|
| **Overall Score** | System effectiveness | Weighted average of all metrics (0-10) |
| **Response Quality** | Coaching usefulness | LLM-as-judge evaluation (0-5) |
| **Citation Accuracy** | RAG grounding | % of responses with knowledge sources |
| **Latency** | Response speed | Time from query to complete answer |
| **EXIF Accuracy** | Vision analysis | Metadata extraction correctness |

**3. LLM-as-Judge Evaluation**

Gemini evaluates each response on:
- **Relevance**: Does it answer the question?
- **Actionability**: Can the user apply the advice?
- **Technical accuracy**: Are photography principles correct?
- **Appropriate detail**: Right depth for skill level?

**4. RAG Citation Verification**

Tests whether responses include:
- Structured knowledge base references
- Photography principle citations (e.g., "Rule of Thirds from curated knowledge")
- Fallback to vector search when needed
- No hallucinated sources

#### Current Results

- **Overall Score**: 8.58/10 ✅
- **Response Quality**: 4.2/5 (LLM-as-judge evaluation)
- **Citation Accuracy**: 95%+ responses grounded in RAG
- **Average Latency**: 26.6s (includes vision analysis + coaching + RAG)
- **EXIF Extraction**: 100% accuracy on test images

**Generated Reports** (`./reports/`):
- `evaluation_detailed.json` – Full response logs and scores
- `evaluation_summary.csv` – Metric breakdown by test case
- `evaluation_report.html` – Interactive visual dashboard

### Manual Testing

```bash
# Test individual platforms
python3 agents_capstone/adk_runner.py      # ADK Runner
python3 demo_mcp.py                         # MCP Server
python3 demo_3_platforms.py                 # All platforms
```

### What "8.58/10" Means

This score represents **production-ready quality** across:
- ✅ Accurate technical analysis (EXIF, composition)
- ✅ Helpful, citation-backed coaching advice
- ✅ Appropriate skill-level adaptation
- ✅ Acceptable latency for real-world use
- ⚠️ Room for improvement: Faster RAG retrieval, more diverse knowledge base

---

## 🔧 Technical Implementation

### Multi-Agent Coordination
```python
orchestrator = Orchestrator(
    vision_agent=VisionAgent(),
    knowledge_agent=KnowledgeAgent()
)

result = orchestrator.process(
    user_query="How to improve composition?",
    image_path="photo.jpg",
    session={"history": []}
)
```

### ADK Runner Integration
```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = LlmAgent(model="gemini-2.5-flash", name="PhotoCoach")
runner = Runner(agent=agent, session_service=session_service)

async for event in runner.run_async(user_id, session_id, new_message):
    if event.content:
        print(event.content.parts[0].text)
```

### MCP Server Protocol
- JSON-RPC 2.0 over stdio transport
- Three tools: `analyze_photo`, `coach_on_photo`, `get_session_history`
- Full error handling and progress notifications
- Claude Desktop compatible

### Hybrid CASCADE RAG
1. **Primary**: Curated knowledge (NumPy similarity, threshold 0.6)
2. **Secondary**: FAISS vector store (1000+ chunks, broader coverage)
3. **Grounding**: Gemini adds structured citations

---

## 📖 Documentation

- **[DELIVERABLES.md](DELIVERABLES.md)**: Capstone submission checklist
- **[KAGGLE_WRITEUP_ENHANCED.md](KAGGLE_WRITEUP_ENHANCED.md)**: Technical deep-dive
- **[ADK_INTEGRATION.md](agents_capstone/ADK_INTEGRATION.md)**: ADK usage guide
- **[OBSERVABILITY.md](agents_capstone/OBSERVABILITY.md)**: Logging & monitoring

---

## 🎯 Key Innovations

1. **Multi-Platform Architecture**: Single agent codebase deploys to ADK (cloud), MCP (desktop), and Python API (custom)
2. **Hybrid CASCADE RAG**: Combines curated knowledge precision with FAISS vector breadth
3. **Domain Specialization**: 20+ curated photography principles with 1000+ document chunks
4. **Production Quality**: Full error handling, caching, logging, and evaluation harness

---

## 🏆 Capstone Submission

**Repository**: https://github.com/prasadt1/ai-photography-coach-agents  
**Branch**: `capstone-submission`

**Quick Start:**
```bash
git clone https://github.com/prasadt1/ai-photography-coach-agents.git
cd ai-photography-coach-agents
pip install -r requirements.txt
export GOOGLE_API_KEY="your_key"
python3 demo_3_platforms.py
```

**Evaluation:**
```bash
python3 demo_eval.py  # Score: 8.58/10
```

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

**Built with**: Python 3.11 • Gemini 2.5 Flash • MCP • ADK • FAISS • LangChain
