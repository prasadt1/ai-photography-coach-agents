import os
from typing import Dict, Any, List
from dotenv import load_dotenv

import streamlit as st
from PIL import Image
import google.generativeai as genai

from agents_capstone.agents.orchestrator import Orchestrator
from agents_capstone.agents.vision_agent import VisionAgent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent
from agents_capstone.logging_config import configure_logging
from agents_capstone.tools import adk_adapter as memory_tool

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="AI Photo Coach", page_icon="📷", layout="wide")

# Configure logging for observability
configure_logging()

# ==================== API KEY AUTHENTICATION ====================
# Allow users to provide their own API key for cost protection
st.sidebar.title("🔑 API Configuration")
st.sidebar.markdown("""
This app uses Google Gemini API. You have two options:

**Option 1: Use Demo Key** (Limited usage)
- Uses a shared demo key
- May hit rate limits if heavily used

**Option 2: Use Your Own Key** (Recommended)
- Get your free API key: [Google AI Studio](https://aistudio.google.com/app/apikey)
- No cost limits from shared usage
""")

use_own_key = st.sidebar.checkbox("I want to use my own API key", value=False)

if use_own_key:
    user_api_key = st.sidebar.text_input(
        "Enter your Google Gemini API Key:",
        type="password",
        help="Your API key will not be stored and is only used for this session"
    )
    if not user_api_key:
        st.warning("⚠️ Please enter your API key in the sidebar to continue")
        st.info("👉 Get your free API key at: https://aistudio.google.com/app/apikey")
        st.stop()
    api_key = user_api_key
    st.sidebar.success("✅ Using your API key")
else:
    # Use environment variable (for demo/development)
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Demo API key not configured. Please use your own API key.")
        st.stop()
    st.sidebar.info("ℹ️ Using shared demo key (may have rate limits)")

# Configure Gemini with the selected API key
genai.configure(api_key=api_key)

# Initialize memory backend (ADK if available, otherwise sqlite)
memory_tool.init()

# Initialize agents
vision_agent = VisionAgent()
knowledge_agent = KnowledgeAgent()
orchestrator = Orchestrator(vision_agent, knowledge_agent)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main > div:first-child {
        padding-top: 1rem;
    }
    
    /* Increase all text sizes */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-size: 1.3em !important;
    }
    
    p, span, div {
        font-size: 16px !important;
    }
    
    /* Chat message styling - User messages (Clean Black & White) */
    .user-message {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #ffffff;
        font-size: 15px !important;
        line-height: 1.5;
    }
    
    .user-message strong {
        color: #ffffff;
        font-size: 16px !important;
    }
    
    /* Chat message styling - Coach messages (Clean Black & White) */
    .coach-message {
        background-color: #2a2a2a;
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #e0e0e0;
        font-size: 15px !important;
        line-height: 1.5;
    }
    
    .coach-message strong {
        color: #ffffff;
        font-size: 16px !important;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px;
        font-size: 16px !important;
    }
    
    /* Caption and labels */
    .stCaption, label {
        font-size: 16px !important;
    }
    
    /* Subheader */
    .stSubheader {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📷 AI Photography Coach")

if "image_path" not in st.session_state:
    st.session_state["image_path"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "last_uploaded_path" not in st.session_state:
    st.session_state["last_uploaded_path"] = None


def run_turn(user_question: str) -> None:
    try:
        base: Dict[str, Any] = orchestrator.run(
            user_id="streamlit_user",
            image_path=st.session_state["image_path"],
            query=user_question,
        )
    except Exception as e:
        st.error(f"Error in orchestrator: {e}")
        return

    vision = base.get("vision")
    coach = base.get("coach", {})

    exif_lines = []
    if vision:
        for k, v in vision.get("exif", {}).items():
            if v is not None:
                exif_lines.append(f"- {k}: {v}")
    exif_block = "\n".join(exif_lines) or "(no EXIF available)"

    summary = vision.get("composition_summary", "(no summary)") if vision else "(no summary)"
    issues_list = coach.get("issues", []) or []
    issues = ", ".join(issues_list) if issues_list else "none"

    coach_text = coach.get("text", "")
    exercise = coach.get("exercise", "")

    prompt = f"""
You are an AI photography mentor.

Vision analysis summary:
{summary}

EXIF:
{exif_block}

Issues detected: {issues}

Coaching suggestions from the analytical agent:
{coach_text}

Practice exercise:
{exercise}

User question: "{user_question}"

Turn this into a friendly, concise answer (max 200 words).
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        with open(st.session_state["image_path"], "rb") as f:
            img_bytes = f.read()
        resp = model.generate_content(
            [
                {"text": prompt},
                {"inline_data": {"data": img_bytes, "mime_type": "image/jpeg"}},
            ]
        )
        answer = (resp.text or "").strip()
        print("DEBUG answer:", answer[:200])
    except Exception as e:
        # If the external model call fails, fall back to a small local FAQ
        # responder so follow-ups (e.g., "what is ISO?") still receive useful
        # answers instead of repeating the same high-level coach text.
        st.session_state["last_error"] = str(e)
        print("DEBUG Gemini error:", e)

        q = (user_question or "").lower()
        def faq_fallback(qtext: str) -> str:
            # Split into sub-questions by common delimiters
            parts = [p.strip() for p in
                     __import__('re').split(r"[\?;\n]+|\band\b|\bthen\b|,", qtext) if p.strip()]
            answers = []

            def single_answer(p: str) -> str:
                p = p.lower()
                if any(k in p for k in ("iso", "iso speed", "isospeed")):
                    return (
                        "ISO controls the camera sensor's sensitivity to light. "
                        "Lower ISO (eg 100) = less sensitivity and less noise; "
                        "higher ISO (eg 800+) increases sensitivity but can add grain/noise."
                    )
                if "aperture" in p or "fnumber" in p or "f-stop" in p or "f/" in p:
                    return (
                        "Aperture (f-number) controls how much light enters the lens and the depth of field. "
                        "Smaller f-number (eg f/1.8) = wider aperture = shallower depth of field; "
                        "larger f-number (eg f/8) = narrower aperture = more of the scene in focus."
                    )
                if "contrast" in p:
                    return (
                        "Contrast describes the difference between bright and dark areas in an image. "
                        "Higher contrast makes shadows darker and highlights brighter; lower contrast yields a flatter look."
                    )
                if "exposure" in p or "expose" in p or "shutter" in p or "shutter speed" in p:
                    return (
                        "Exposure is the total brightness of the image determined by aperture, shutter speed, and ISO. "
                        "Use faster shutter speeds to freeze motion and slower to allow motion blur. Balance exposure to avoid blown highlights or blocked shadows."
                    )
                if "rule of thirds" in p or "rule of 3" in p or "third" in p:
                    return (
                        "The Rule of Thirds is a composition guideline: imagine a 3×3 grid and place key elements on the grid lines or intersections. "
                        "This usually creates a more dynamic and balanced composition than centering the subject."
                    )
                if "depth of field" in p or "depth" in p:
                    return (
                        "Depth of field is how much of the scene appears acceptably sharp. Wider apertures (small f-numbers) give shallower depth of field; smaller apertures increase depth of field."
                    )
                # No match: return empty so we can fallback later
                return ""

            for part in parts:
                ans = single_answer(part)
                if ans:
                    answers.append(ans)

            if answers:
                # Return combined unique answers
                seen = set()
                combined = []
                for a in answers:
                    if a not in seen:
                        combined.append(a)
                        seen.add(a)
                return "\n\n".join(combined)

            # Generic fallback uses the coach text if available, else a minimal message
            if coach_text:
                return coach_text
            return "(No assistant response available due to an internal error.)"

        answer = faq_fallback(q)
        # continue rather than returning so chat_history gets appended

    try:
        print("DEBUG before append, history len:", len(st.session_state.get("chat_history", [])))
        st.session_state["last_result"] = base
        # Ensure chat_history exists and is a list
        if "chat_history" not in st.session_state or not isinstance(st.session_state.get("chat_history"), list):
            st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({"role": "user", "content": user_question})
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        print("DEBUG after append, history len:", len(st.session_state.get("chat_history", [])))
        # record a small debug trace
        st.session_state.setdefault("last_debug_logs", []).append({"user": user_question, "assistant_preview": answer[:120]})
    except Exception as e:
        st.session_state["last_error"] = f"Error appending chat history: {e}"
        print("DEBUG append error:", e)


# ---------- UI LAYOUT ----------

col_left, col_right = st.columns([1.1, 1.4])

with col_left:
    st.subheader("1️⃣ Upload & Review")
    uploaded = st.file_uploader("📸 Choose a photo (JPG/JPEG)", type=["jpg", "jpeg"])

    if uploaded is not None:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Current photo", use_column_width=True)

        tmp_path = "tmp_uploaded.jpg"
        # Save the image while preserving EXIF data
        try:
            if hasattr(uploaded, 'read'):
                # Save original bytes directly to preserve EXIF
                with open(tmp_path, "wb") as f:
                    f.write(uploaded.getbuffer())
            else:
                img.save(tmp_path, format="JPEG")
        except Exception:
            # Fallback to simple save
            img.save(tmp_path, format="JPEG")
        
        # Only reset history if a NEW image is being uploaded
        if st.session_state["last_uploaded_path"] != uploaded.name:
            st.session_state["image_path"] = tmp_path
            st.session_state["chat_history"] = []
            st.session_state["last_result"] = None
            st.session_state["last_uploaded_path"] = uploaded.name
        else:
            st.session_state["image_path"] = tmp_path
        
        # Display photo info
        st.divider()
        st.caption(f"📁 File: {uploaded.name}")
        st.caption(f"📏 Size: {img.size[0]} × {img.size[1]} pixels")
        
        # Run initial vision analysis on photo upload if we haven't already
        if st.session_state["last_result"] is None:
            try:
                base = orchestrator.run(
                    user_id="streamlit_user",
                    image_path=st.session_state["image_path"],
                    query="Analyze this photo",
                )
                st.session_state["last_result"] = base
            except Exception as e:
                st.error(f"Error analyzing photo: {e}")
        
        # Show analysis results if available
        if st.session_state["last_result"]:
            result = st.session_state["last_result"]
            vision = result.get("vision", {})
            coach = result.get("coach", {})
            
            # Display Composition Summary
            if vision:
                st.write("**📝 Composition:**")
                st.caption(vision.get("composition_summary", "N/A"))
            
            # Display EXIF Data prominently
            if vision:
                exif = vision.get("exif", {})
                if exif and any(v is not None for v in exif.values() if v != "error"):
                    st.write("**📸 EXIF Data:**")
                    exif_cols = st.columns(2)
                    exif_items = [(k, v) for k, v in exif.items() if v is not None and k != "error"]
                    for idx, (k, v) in enumerate(exif_items):
                        with exif_cols[idx % 2]:
                            st.caption(f"**{k}:** {v}")
                else:
                    st.caption("*No EXIF data available for this image*")
            
            # Display Issues
            if coach:
                issues = coach.get("issues", [])
                if issues:
                    st.write("**⚠️ Issues Detected:**")
                    for issue in issues:
                        st.caption(f"• {issue}")
    else:
        st.info("👆 Upload a photo to get started!", icon="ℹ️")


with col_right:
    st.subheader("2️⃣ Chat with your Coach")

    if st.session_state["image_path"] is None:
        st.info("👈 Upload a photo on the left to start chatting!", icon="ℹ️")
    else:
        # Display chat messages
        if len(st.session_state["chat_history"]) > 0:
            st.write("**Conversation:**")
            for turn in st.session_state["chat_history"]:
                if turn["role"] == "user":
                    st.markdown(f"<div class='user-message'><strong>👤 You:</strong><br>{turn['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='coach-message'><strong>🏆 Coach:</strong><br>{turn['content']}</div>", unsafe_allow_html=True)
            st.divider()
        
        # Input area
        question_default = (
            "How can I improve this composition?"
            if not st.session_state["chat_history"]
            else ""
        )
        question = st.text_area(
            "✍️ Ask your coach:",
            value=question_default,
            height=80,
            placeholder="Ask about composition, lighting, ISO, framing...",
            key="chat_input"
        )

        col_btn1, col_btn2 = st.columns([0.35, 0.65])
        with col_btn1:
            analyze = st.button("🚀 Analyze", type="primary")
        with col_btn2:
            st.caption(
                "💡 Try: 'How should I reframe?', 'What about the lighting?', 'ISO suggestions?'"
            )

        if analyze and question.strip():
            with st.spinner("🤔 Coach is thinking..."):
                run_turn(question.strip())
            # Force rerun to display the new messages immediately
            st.rerun()
        
        # -- Developer diagnostics (collapse to view) --
        with st.expander("Debug: session state", expanded=False):
            st.write("chat_history:")
            st.write(st.session_state.get("chat_history"))
            st.write("last_result keys:")
            last = st.session_state.get("last_result")
            if last is None:
                st.write(None)
            else:
                st.write(list(last.keys()))
        
        # Observability panel (persisted memory + logs)
        with st.expander("Observability", expanded=False):
            # Filter out credential errors (expected when not using Google Cloud)
            last_err = st.session_state.get("last_error")
            if last_err and "default credentials" not in str(last_err).lower():
                st.write("last_error:", last_err)
            st.write("last_debug_logs:", st.session_state.get("last_debug_logs"))
            # show compacted summary from persisted session if available
            if st.session_state.get("image_path"):
                user_id = "streamlit_user"
                persisted = memory_tool.get_value(user_id, "session")
                if persisted:
                    st.write("persisted session keys:", list(persisted.keys()))
                    st.write("compact_summary:", persisted.get("compact_summary"))
