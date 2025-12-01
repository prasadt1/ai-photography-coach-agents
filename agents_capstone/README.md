# 📸 AI Photography Coach – Capstone (Gemini + Agents)

This folder contains the **Google AI Agents Intensive capstone** version of the AI Photography Coach:  
an **agentic, Gemini‑powered** mentor that analyzes photos, reads EXIF metadata, and supports interactive Q&A in a Streamlit UI.

> The root of this repo contains the original **RAG‑only, local tinyllama** version.  
> This capstone version focuses on **Gemini, multi‑agent design, and an interactive coaching experience**.

---

## 🎯 Problem

Learning photography is hard:

- Beginners struggle to connect abstract rules (rule of thirds, leading lines, ISO triangle) to their own images.  
- Existing AI tools mostly **edit or cull** photos; they rarely explain *why* an image works or how to improve it.  
- Generic chatbots don’t see your photo, ignore EXIF, and often hallucinate technical advice.

---

## 💡 Capstone Solution

An **AI Photography Coach** that behaves like a mentor:

- Looks at your actual photo (Gemini Vision).  
- Understands your **camera settings** (EXIF).  
- Provides **image‑specific feedback** on composition and exposure.  
- Supports **follow‑up questions** in a conversational loop.

Key design goals for the capstone:

- Showcase **Gemini 2.5 Vision** and **Google AI tooling**.  
- Use an **agent‑like separation of concerns** (Vision + Coaching).  
- Provide a simple **Streamlit app** for judges to try locally.

---

## 🧩 Architecture (Capstone Variant)
```text
User + Photo
      ↓
Streamlit UI (app_streamlit.py)
      ↓
VisionAgent (Gemini Vision + EXIF)
      ↓
VisionAnalysis { exif, composition_summary, issues[] }
      ↓
ChatCoach (Gemini text + image, multi‑turn)
      ↓
Interactive coaching replies
```

### Components

- **VisionAgent (`agents/vision_agent.py`)**
  - Extracts EXIF (camera, focal length, aperture, ISO, shutter).
  - Calls **Gemini 2.5 Flash** with the image and EXIF.
  - Produces a structured `VisionAnalysis` with:
    - `composition_summary`: short natural‑language critique.
    - `exif`: cleaned metadata.
    - `issues`: simple tags (e.g., `subject_centered`, `horizon_tilt`, `high_iso`).

- **ChatCoach (`agents/chat_coach.py`)**
  - Builds prompts from:
    - Vision summary,
    - EXIF,
    - prior conversation turns,
    - new user question.
  - Sends **image + prompt** to Gemini each turn for context‑aware replies.

- **Streamlit UI (`app_streamlit.py`)**
  - Handles image upload and preview.
  - Caches the **first‑pass VisionAnalysis** per image.
  - Maintains `st.session_state["history"]` for a chat‑like experience.
  - Shows:
    - EXIF + composition summary,
    - ongoing Q&A with the coach.

- **Tools (`tools/exif_tool.py`, `tools/knowledge_base.py`)**
  - EXIF extraction for camera settings.
  - Optional RAG retrieval (used more in the original RAG app and ADK flows).

---

## 🏗️ Folder Structure (Capstone)

```text
agents_capstone/
├── app_streamlit.py          # Streamlit web demo for the capstone
├── agents/
│   ├── vision_agent.py       # Gemini Vision + EXIF → VisionAnalysis
│   ├── chat_coach.py         # Multi-turn coaching using Gemini
│   ├── knowledge_agent.py    # RAG + structured coaching (used in ADK version)
│   └── orchestrator.py       # Orchestrator for ADK / multi-agent flows
├── tools/
│   ├── exif_tool.py          # EXIF parsing and formatting helpers
│   └── knowledge_base.py     # Simple retrieval over photography notes
└── README.md                 # This file
```
---

## 🚀 Running the Capstone Demo (Streamlit + Gemini)

### 1. Install dependencies

From the repo root:
cd ai-photography-coach-rag

python3 -m pip install -r requirements.txt

Make sure `google-generativeai` is installed (it is in `requirements.txt`).

### 2. Configure Gemini

Export your Gemini API key (same as in Kaggle/ADK):

export GOOGLE_API_KEY="YOUR_GEMINI_KEY"

### 3. Start the Streamlit app

Open the printed URL (usually `http://localhost:8501`).

### 4. Use the app

1. Upload a JPEG from your camera/phone (with EXIF).  
2. Ask an initial question, e.g.  
   `How can this shot be improved?`  
3. Ask follow‑ups, for example:
   - `What ISO would you use for this scene?`
   - `How should I reframe this to avoid the lamppost?`
   - `What would change if I shoot this at sunset?`

Under the hood:

- The **first turn** runs `VisionAgent.analyze(...)` once and stores `VisionAnalysis` in session state.  
- Every turn builds a new prompt with:
  - photo,
  - composition summary,
  - EXIF,
  - conversation history,
  - current question,  
  and calls Gemini for a fresh answer.

---

## 🎓 How It Maps to the Capstone Rubric

- **Use of Gemini:**  
  - Gemini 2.5 Flash is used both for image understanding and conversational coaching.

- **Agentic Design:**  
  - Clear separation between **VisionAgent** and **ChatCoach**, with optional orchestrator in the ADK version.

- **Reasoning & Evaluation:**  
  - Vision summary plus issue tags (`issues[]`) provide structured signals that can be logged or evaluated.  
  - Follow‑up questions demonstrate **context retention** and reasoning over multiple turns.

- **End‑to‑End Experience:**  
  - Streamlit UI makes the project accessible to non‑technical users and judges.  
  - The same components can be wired into a Kaggle notebook via ADK for the formal submission.

---

## 🔮 Future Enhancements (Capstone Roadmap)

- Add an explicit **RAG agent** that surfaces definitions and visual examples from a photography corpus.  
- Add **user profiles** (beginner / intermediate / advanced) to adapt explanations.  
- Integrate basic **evaluation metrics** (e.g., log issues, track improvement suggestions).

---

**Built for the Google AI Agents Intensive – Capstone Project**  
**Demonstrates:** Gemini Vision • Agentic Design • Interactive Coaching • EXIF‑aware Reasoning
