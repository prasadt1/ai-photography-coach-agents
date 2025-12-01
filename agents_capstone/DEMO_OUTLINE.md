# Demo Outline – AI Photography Coach

This document outlines a short walkthrough and optional video shots for demonstrating the AI Photography Coach capstone project.

---

## 5-Minute Walkthrough

### 1. Opening (30 seconds)
- **Screen:** Streamlit app homepage
- **Narrative:** "This is the AI Photography Coach, an agentic system that analyzes your photos and provides personalized coaching using Gemini Vision and a multi-agent orchestrator."
- **Show:** Title, app layout with left (image) and right (chat) panels

### 2. Image Upload & EXIF (1 minute)
- **Action:** Upload a high-quality JPEG from a camera or phone (with EXIF metadata)
- **Show:** 
  - Image preview in left panel
  - EXIF metadata appears (Model, FocalLength, ISO, etc.)
  - Composition summary below
  - Any detected issues (e.g., "subject_centered", "high_iso")
- **Narrative:** "Notice the camera settings are automatically extracted and analyzed. The system identifies areas for improvement."

### 3. First Question (1 minute)
- **Action:** Type a question: *"How can I improve the composition of this photo?"*
- **Show:**
  - Question appears in chat
  - Coach response with multi-sentence coaching advice
  - Response includes actionable tips (e.g., "Consider using the rule of thirds by moving the subject left...")
- **Narrative:** "The coach provides specific, image-aware feedback based on the composition analysis and camera settings."

### 4. Follow-Up Question (1 minute)
- **Action:** Type a follow-up: *"What is ISO and how does it affect image quality?"*
- **Show:**
  - Chat history persists; both questions and answers visible
  - New coach response references the photo and prior context
- **Narrative:** "The coach maintains conversation history and can answer follow-up questions. Notice how it ties feedback to the image."

### 5. Observability & Debug (1 minute)
- **Action:** Scroll to right side, click "Debug & Observability" expander
- **Show:**
  - Session ID and skill level
  - Latency of each agent call (Vision ~2s, Knowledge ~3s)
  - Compact summary of the conversation
  - Recent JSON logs
- **Narrative:** "Behind the scenes, we're tracking latency, session state, and detailed logs for every agent call. This enables observability and debugging."

### 6. Closing (30 seconds)
- **Show:** "Learn more..." links to WRITEUP.md, ADK_INTEGRATION.md
- **Narrative:** "This demo showcases a production-ready multi-agent system with session management, persistent memory, and observability—built on Gemini and the Agent Development Kit."

---

## Optional: 30-Second Video Shots

If producing a short demo video, capture these shots in sequence:

### Shot 1: Intro (3 seconds)
- Fade in to Streamlit app title: "📸 AI Photography Coach"
- Text overlay: "Multi-Agent Coaching System Powered by Gemini"

### Shot 2: Image Upload (5 seconds)
- Show file browser → select high-quality photo
- Upload completes → image preview + EXIF metadata appears
- Zoom in on EXIF fields briefly (Model, ISO, Focal Length)

### Shot 3: Composition Analysis (4 seconds)
- Show composition summary and detected issues
- Pan down to see full analysis

### Shot 4: First Question (6 seconds)
- Type first question in chat
- Show coach response appearing with smooth scroll
- Text overlay: "Image-Aware, Multi-Turn Coaching"

### Shot 5: Follow-Up Question (6 seconds)
- Type follow-up question
- Show coach response, demonstrating context retention
- Briefly highlight chat history

### Shot 6: Observability (4 seconds)
- Expand Debug & Observability panel
- Show latency metrics, session state, logs
- Text overlay: "Built-In Observability & Logging"

### Shot 7: Architecture Diagram (2 seconds)
- Static slide showing: User → VisionAgent → KnowledgeAgent → Response
- Text: "Sequential Multi-Agent Orchestration"

### Shot 8: Closing (2 seconds)
- Fade to project title with repository link
- Text: "Built for Google AI Agents Intensive Capstone"

---

## Running Locally for Demo

### Prerequisites
```bash
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
export PYTHONPATH=$PWD:$PYTHONPATH
cd /Users/prasadt1/ai-photography-coach-rag
```

### Start the App
```bash
python3 -m streamlit run agents_capstone/app_streamlit.py
```

- Opens at `http://localhost:8501`
- No authentication required
- Session data persists to local SQLite (`agents_memory.db`)

### Run Evaluation

**From project root:**
```bash
python3 run_evaluation.py
```

**Or from agents_capstone/ (quick version):**
```bash
cd agents_capstone
python3 quick_eval.py
```

Reports are saved to `reports/` with HTML dashboard for easy viewing.

### Test Images Recommended

For best demo results, use photos that:
- Have **visible EXIF metadata** (from a camera or smartphone)
- Show **clear composition** (interesting subject placement, lighting, depth)
- Have **some issue** (e.g., centered subject, high ISO, overexposed) so coaching is relevant

**Example good demo photos:**
- Landscape with horizon
- Portrait with background
- Action/sports shot
- Indoor with mixed lighting

---

## Script Template

**[Opening]**
"Hello, I'm [Name]. Today I want to show you the **AI Photography Coach**, a capstone project for the Google AI Agents Intensive course. It's a multi-agent system that analyzes your photos and provides personalized coaching."

**[Upload Image]**
"Let me upload a photo I took with my camera. Notice how the app instantly extracts the EXIF metadata—camera model, ISO, focal length—and provides a composition analysis."

**[First Question]**
"Now I'll ask the coach for feedback on composition. Watch as it provides specific, actionable advice based on both the image analysis and the camera settings."

**[Follow-Up]**
"Let me ask a follow-up question about ISO. The coach remembers our conversation and ties its answer back to my photo. This multi-turn context is powered by **session management** and **multi-agent orchestration**."

**[Observability]**
"Behind the scenes, we're logging every agent call and tracking metrics. You can see latency, session state, and even the compact summary of our conversation. This is critical for production systems."

**[Closing]**
"This project demonstrates the full capstone rubric: multi-agent design (Day 1), custom tools (Day 2), session & memory (Day 3), observability & evaluation (Day 4), and production deployment (Day 5). All code is available at [GitHub link]."

---

## Screenshots to Capture

1. **App Overview**
   - Full Streamlit layout with image and chat panels visible

2. **EXIF Metadata**
   - Close-up of EXIF table showing camera details

3. **Coaching Response**
   - Chat with question + detailed coach response

4. **Multi-Turn Chat**
   - Chat history showing 3–4 turns of conversation

5. **Observability Panel**
   - Debug & Observability expander open, showing metrics and logs

6. **Evaluation Report**
   - HTML report from `evaluate.py` (opened in browser)

---

## Suggested Presentation Context

- **5-minute live demo** at capstone showcase
- **30-second elevator pitch video** for social media
- **3-minute recorded walkthrough** for async review
- **Interactive Jupyter notebook** (`capstone_demo.ipynb`) for judges to run locally

---

## Backup Plan (If Live Demo Fails)

If the live app crashes or API is unavailable:

1. **Pre-record a video** of the walkthrough
2. **Show screenshots** and walk through them manually
3. **Display the code** and explain the architecture
4. **Run the evaluation script** to show scoring output
5. **Link to GitHub** for live code review

---

## Key Talking Points

- ✅ **Multi-Agent Architecture:** Demonstrates separation of concerns (Vision + Knowledge agents)
- ✅ **Gemini Integration:** Shows real image understanding and conversational AI
- ✅ **Session Management:** Explains how context persists across turns
- ✅ **Observability:** Points out logging, metrics, and debugging capabilities
- ✅ **Production Ready:** Docker deployment, error handling, evaluation framework
- ✅ **ADK Compatible:** Mentions transparent ADK integration for cloud deployment

---

**Built for:** Google AI Agents Intensive – Capstone Project
