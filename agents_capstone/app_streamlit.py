import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv

import streamlit as st
from PIL import Image
import google.generativeai as genai

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_capstone.agents.orchestrator import Orchestrator
from agents_capstone.agents.vision_agent import VisionAgent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent
from agents_capstone.logging_config import configure_logging
from agents_capstone.tools import adk_adapter as memory_tool

# Load environment variables from .env file (look in project root)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

st.set_page_config(page_title="AI Photo Coach", page_icon="📷", layout="wide")

# Configure logging for observability
configure_logging()

# ==================== API KEY AUTHENTICATION ====================
# Require users to provide their own API key for public deployment
st.sidebar.title("🔑 Setup Required")
st.sidebar.markdown("""
To use this AI Photography Coach, a **free** Google Gemini API key is required.

### How to obtain an API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account
3. Click "Create API Key"
4. Copy and paste it below

**Note:** API keys are never stored and only used during the session.
""")

user_api_key = st.sidebar.text_input(
    "Google Gemini API Key:",
    type="password",
    value=os.getenv("GOOGLE_API_KEY", ""),
    help="Obtain free API key at: https://aistudio.google.com/app/apikey"
)

if not user_api_key:
    st.warning("⚠️ **API Key Required**")
    st.info("""
    This app needs a Google Gemini API key to function. Don't worry - it's completely free!
    
    **Steps to get started:**
    1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Create a free API key (takes ~30 seconds)
    3. Paste it in the sidebar (or add to .env file)
    4. Start getting photography coaching!
    """)
    st.stop()

st.sidebar.success("✅ API key configured")

# Configure Gemini with the user's API key
# IMPORTANT: Must configure BEFORE initializing agents
genai.configure(api_key=user_api_key)

# Initialize memory backend (ADK if available, otherwise sqlite)
memory_tool.init()

# Cache agent initialization to avoid reloading on every interaction
# This speeds up subsequent requests by ~5-10 seconds
@st.cache_resource(show_spinner="🤖 Initializing AI agents (first time: ~10 seconds)...")
def get_orchestrator(_api_key):
    """Initialize agents once and cache them across requests
    
    Note: _api_key parameter ensures cache is keyed by API key,
    so different users don't share the same model instance
    """
    # Reconfigure genai in case cache was from different API key
    genai.configure(api_key=_api_key)
    vision = VisionAgent()
    knowledge = KnowledgeAgent()
    return Orchestrator(vision, knowledge)

orchestrator = get_orchestrator(user_api_key)
# For backward compatibility
vision_agent = orchestrator.vision_agent
knowledge_agent = orchestrator.knowledge_agent

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

    # Get coaching text which already has RAG citations from KnowledgeAgent
    coach_text = coach.get("text", "")
    exercise = coach.get("exercise", "")

    # Use the coach_text directly - it already has Agentic RAG citations!
    # No need for another Gemini pass that would strip out the citations
    answer = coach_text
    
    # Add exercise if available
    if exercise:
        answer += f"\n\n**💪 Practice Exercise:** {exercise}"
    
    print("DEBUG answer with citations:", answer[:300])
    
    # Fallback if coaching is empty (shouldn't happen with working agent)
    if not answer or answer.strip() == "":
        print("DEBUG: Empty coach response, using FAQ fallback")
        answer = "(No coaching response available. Try again or check the image.)"

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

# Create a placeholder at the VERY TOP for progress indicator (outside columns)
status_placeholder = st.empty()

col_left, col_right = st.columns([1.1, 1.4])

with col_left:
    st.subheader("1️⃣ Upload & Review")
    uploaded = st.file_uploader("📸 Choose a photo (JPG/JPEG)", type=["jpg", "jpeg"], 
                                 help="Analysis takes ~5-10 seconds on first upload")

    if uploaded is not None:
        # Process image upload
        img = Image.open(uploaded).convert("RGB")
        
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
        
        # Display image
        st.image(img, caption="Current photo", use_column_width=True)
        
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
            # Show status at the TOP of page using placeholder
            with status_placeholder.status("🔍 Analyzing photo...", expanded=False) as status:
                try:
                    base = orchestrator.run(
                        user_id="streamlit_user",
                        image_path=st.session_state["image_path"],
                        query="Analyze this photo",
                    )
                    
                    st.session_state["last_result"] = base
                    status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                    
                except Exception as e:
                    status.update(label="❌ Analysis failed", state="error", expanded=False)
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
            "✍️ Ask the coach:",
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
            with st.spinner("🤔 Analyzing photo & searching knowledge base..."):
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
