"""
Admin UI for AI Photography Coach Knowledge Base Management

This is a production-style admin interface for:
- Uploading PDFs to knowledge base
- Rebuilding FAISS vector index
- Monitoring knowledge base status
- Viewing retrieval statistics

Architecture Pattern:
---------------------
In production systems, knowledge base indexing should NOT happen
during normal user sessions. Instead:

1. Admin uploads PDFs via this UI (or Cloud Storage trigger)
2. Index rebuilding runs offline (takes 2-3 minutes)
3. Main app loads pre-built index instantly
4. Users get fast responses without waiting for indexing

This separation ensures:
✅ No user-facing latency from indexing
✅ Control over knowledge base updates
✅ Ability to review/approve content before indexing
✅ Scheduled updates (nightly, weekly, etc.)

Usage:
------
Local: python3 -m streamlit run agents_capstone/admin_ui.py
Cloud: Deploy as separate Cloud Run service with auth
"""

import streamlit as st
import os
from pathlib import Path
import shutil
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Admin - AI Photography Coach",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Knowledge Base Admin")
st.markdown("*Manage photography knowledge sources and vector indices*")

# Paths
DATA_DIR = Path("agents_capstone/data/pdfs")
INDEX_DIR = Path("agents_capstone/data/faiss_index")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize session state
if 'index_status' not in st.session_state:
    st.session_state.index_status = None
if 'rebuild_log' not in st.session_state:
    st.session_state.rebuild_log = []


# Helper functions
def get_index_stats():
    """Get statistics about current index"""
    try:
        from tools.faiss_store import get_faiss_store
        store = get_faiss_store()
        stats = store.get_stats()
        return stats
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_pdf_files():
    """List all PDFs in data directory"""
    if not DATA_DIR.exists():
        return []
    return sorted([f.name for f in DATA_DIR.glob("*.pdf")])


def get_curated_stats():
    """Get stats about curated knowledge base"""
    try:
        from data.knowledge_sources import PHOTOGRAPHY_KNOWLEDGE
        categories = {}
        for entry in PHOTOGRAPHY_KNOWLEDGE:
            cat = entry["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_entries": len(PHOTOGRAPHY_KNOWLEDGE),
            "categories": categories,
            "status": "loaded"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard", 
    "📤 Upload PDFs", 
    "🔄 Rebuild Index",
    "📈 Statistics"
])


# ============ TAB 1: DASHBOARD ============
with tab1:
    st.header("Knowledge Base Status")
    
    col1, col2 = st.columns(2)
    
    # Curated Knowledge
    with col1:
        st.subheader("🎯 PRIMARY: Curated Knowledge")
        curated_stats = get_curated_stats()
        
        if curated_stats["status"] == "loaded":
            st.metric("Total Entries", curated_stats["total_entries"])
            st.markdown("**Categories:**")
            for cat, count in curated_stats["categories"].items():
                st.markdown(f"- {cat}: {count}")
            st.success("✅ Curated knowledge loaded")
        else:
            st.error(f"❌ Error: {curated_stats.get('error', 'Unknown')}")
    
    # FAISS Index
    with col2:
        st.subheader("📚 SECONDARY: FAISS PDF Index")
        faiss_stats = get_index_stats()
        
        if faiss_stats["status"] == "loaded":
            st.metric("Total Vectors", f"{faiss_stats['total_vectors']:,}")
            st.metric("Index Size", f"{faiss_stats['index_size_mb']} MB")
            
            # Last modified time
            if INDEX_DIR.exists():
                mod_time = datetime.fromtimestamp(INDEX_DIR.stat().st_mtime)
                st.markdown(f"**Last Updated:** {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            st.success("✅ FAISS index loaded")
        elif faiss_stats["status"] == "not_loaded":
            if faiss_stats.get("index_exists"):
                st.warning("⚠️ Index exists but not loaded")
                if st.button("Load Index"):
                    with st.spinner("Loading FAISS index..."):
                        from tools.faiss_store import get_faiss_store
                        store = get_faiss_store()
                        if store.load_index():
                            st.success("✅ Index loaded!")
                            st.rerun()
            else:
                st.info("ℹ️ No index found. Upload PDFs and rebuild.")
        else:
            st.error(f"❌ Error: {faiss_stats.get('error', 'Unknown')}")
    
    # PDF Files
    st.divider()
    st.subheader("📄 PDF Files in Knowledge Base")
    pdf_files = get_pdf_files()
    
    if pdf_files:
        st.markdown(f"**{len(pdf_files)} PDF(s) available:**")
        for pdf in pdf_files:
            file_path = DATA_DIR / pdf
            size_mb = file_path.stat().st_size / (1024 * 1024)
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"📄 {pdf}")
            col2.markdown(f"*{size_mb:.2f} MB*")
            if col3.button("🗑️", key=f"delete_{pdf}"):
                file_path.unlink()
                st.success(f"Deleted {pdf}")
                st.rerun()
    else:
        st.info("No PDFs uploaded yet. Use the Upload tab to add knowledge sources.")


# ============ TAB 2: UPLOAD PDFS ============
with tab2:
    st.header("📤 Upload Photography Knowledge PDFs")
    
    st.markdown("""
    Upload PDF files containing photography knowledge:
    - Photography guides and handbooks
    - Composition tutorials
    - Technical manuals
    - Educational materials
    
    ⚠️ **Note:** After uploading, you must rebuild the index in the next tab.
    """)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        
        for uploaded_file in uploaded_files:
            st.markdown(f"- {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("💾 Save to Knowledge Base", type="primary"):
            with st.spinner("Saving files..."):
                saved_count = 0
                for uploaded_file in uploaded_files:
                    # Save to data directory
                    target_path = DATA_DIR / uploaded_file.name
                    
                    if target_path.exists():
                        st.warning(f"⚠️ {uploaded_file.name} already exists, skipping")
                        continue
                    
                    with open(target_path, 'wb') as f:
                        f.write(uploaded_file.read())
                    
                    saved_count += 1
                    st.success(f"✅ Saved {uploaded_file.name}")
                
                st.success(f"🎉 Saved {saved_count} file(s)!")
                st.info("👉 Go to 'Rebuild Index' tab to index these PDFs")


# ============ TAB 3: REBUILD INDEX ============
with tab3:
    st.header("🔄 Rebuild FAISS Vector Index")
    
    st.markdown("""
    This process:
    1. Loads all PDFs from the knowledge base
    2. Splits them into chunks (1000 chars, 150 overlap)
    3. Generates embeddings using `all-MiniLM-L6-v2`
    4. Creates FAISS index for fast similarity search
    
    ⏱️ **Time:** 2-3 minutes for 6 PDFs
    
    ⚠️ **Warning:** This will overwrite the existing index!
    """)
    
    pdf_files = get_pdf_files()
    
    if not pdf_files:
        st.warning("⚠️ No PDFs found. Upload PDFs first in the Upload tab.")
    else:
        st.success(f"✅ Found {len(pdf_files)} PDF(s) ready for indexing")
        
        with st.expander("📄 Files to be indexed"):
            for pdf in pdf_files:
                st.markdown(f"- {pdf}")
        
        if st.button("🚀 Rebuild Index Now", type="primary"):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.container()
            
            def update_progress(step, total, message):
                """Callback for progress updates"""
                progress = int((step / total) * 100)
                progress_bar.progress(progress)
                status_text.markdown(f"**{message}** ({step}/{total})")
                log_container.markdown(f"- {message}")
            
            try:
                from tools.faiss_store import get_faiss_store
                
                status_text.markdown("**Starting index rebuild...**")
                log_container.markdown("### 📝 Rebuild Log")
                
                store = get_faiss_store()
                success = store.ingest_pdfs(progress_callback=update_progress)
                
                if success:
                    progress_bar.progress(100)
                    st.balloons()
                    st.success("🎉 Index rebuilt successfully!")
                    st.info("The new index is now active. Go to Dashboard to verify.")
                else:
                    st.error("❌ Index rebuild failed. Check logs above.")
                    
            except Exception as e:
                st.error(f"❌ Error during rebuild: {e}")
                st.exception(e)


# ============ TAB 4: STATISTICS ============
with tab4:
    st.header("📈 Knowledge Base Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Curated Knowledge")
        curated_stats = get_curated_stats()
        
        if curated_stats["status"] == "loaded":
            st.json(curated_stats)
        else:
            st.error(f"Error: {curated_stats.get('error')}")
    
    with col2:
        st.subheader("📚 FAISS Index")
        faiss_stats = get_index_stats()
        st.json(faiss_stats)
    
    # Test Search
    st.divider()
    st.subheader("🔍 Test Knowledge Retrieval")
    
    test_query = st.text_input(
        "Enter a photography question:",
        placeholder="e.g., rule of thirds, golden hour, depth of field"
    )
    
    col1, col2 = st.columns(2)
    test_curated = col1.button("Search Curated")
    test_faiss = col2.button("Search FAISS")
    
    if test_curated and test_query:
        st.markdown("### 🎯 Curated Knowledge Results")
        try:
            from tools.agentic_rag import AgenticRAG
            rag = AgenticRAG(enable_faiss=False)
            results = rag.retrieve_grounding(test_query, top_k=3)
            
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i} - Score: {result['relevance_score']:.3f}"):
                    st.markdown(f"**Source:** {result['source']}")
                    st.markdown(f"**Category:** {result['category']}")
                    st.markdown(f"**Text:**\n{result['text']}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if test_faiss and test_query:
        st.markdown("### 📚 FAISS PDF Results")
        try:
            from tools.faiss_store import get_faiss_store
            store = get_faiss_store()
            
            if store.db is None:
                st.warning("FAISS index not loaded")
            else:
                results = store.search(test_query, k=3)
                
                for i, result in enumerate(results, 1):
                    with st.expander(f"Result {i} - Score: {result['score']:.3f}"):
                        st.markdown(f"**Source:** {result['source']}")
                        st.markdown(f"**Text:**\n{result['text'][:300]}...")
        except Exception as e:
            st.error(f"Error: {e}")


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>AI Photography Coach - Admin Interface</p>
    <p>For production use: Add authentication, rate limiting, and audit logging</p>
</div>
""", unsafe_allow_html=True)
