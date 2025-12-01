# Media Gallery Recommendations for Kaggle Submission

## Required Screenshots (4 recommended)

### Screenshot 1: Streamlit UI with EXIF Metadata
**What to capture:**
- Upload a sample photo (preferably landscape or portrait with good EXIF data)
- Show the EXIF panel displaying:
  - Camera Model (e.g., "Canon EOS R5")
  - ISO (e.g., "ISO 400")
  - Aperture (e.g., "f/2.8")
  - Shutter Speed (e.g., "1/500s")
  - Focal Length (e.g., "85mm")
- Ensure the uploaded photo is visible
- Caption: "Streamlit web interface showing real-time EXIF metadata extraction"

**How to take:**
```bash
cd /Users/prasadt1/ai-photography-coach-agents
python3 -m streamlit run agents_capstone/app_streamlit.py
# Upload a photo, then screenshot the main interface
```

---

### Screenshot 2: Dynamic Chat Response
**What to capture:**
- Chat panel showing a user question like "How can I improve composition?"
- Dynamic LLM response that:
  - References the specific image
  - Mentions detected issues (e.g., "centered subject")
  - Provides actionable advice
  - Shows it's contextual (not a template)
- Caption: "Context-aware coaching powered by Gemini 1.5 Flash with conversation history"

**How to take:**
```bash
# In the Streamlit app, after uploading a photo:
# 1. Type: "How can I improve composition?"
# 2. Wait for response
# 3. Screenshot the chat panel showing both question and response
```

---

### Screenshot 3: Debug Panel & Observability
**What to capture:**
- Click "🔍 Debug & Observability" expander
- Show the debug panel displaying:
  - Current session ID
  - Number of turns in conversation
  - Agent call traces (VisionAgent → KnowledgeAgent)
  - Latency metrics
  - Session state
- Caption: "Production-grade observability with structured logging and debug panel"

**How to take:**
```bash
# In the Streamlit app:
# 1. Expand the "Debug & Observability" section
# 2. Scroll to show all metrics
# 3. Screenshot the entire debug panel
```

---

### Screenshot 4: Evaluation Report
**What to capture:**
- Open the HTML evaluation report (`agents_capstone/reports/evaluation_report.html`)
- Show the dashboard displaying:
  - Score table with 4 dimensions (Relevance, Completeness, Accuracy, Actionability)
  - Average scores
  - Individual test scenario results
  - Color-coded scores (green for high, yellow for medium)
- Caption: "LLM-as-Judge evaluation framework with automated quality scoring"

**How to take:**
```bash
# Generate fresh evaluation report:
cd /Users/prasadt1/ai-photography-coach-agents
python3 demo_eval.py

# Open in browser:
open agents_capstone/reports/evaluation_report.html

# Screenshot the full dashboard
```

---

## Optional: Demo Video (60-90 seconds)

### Video Script

**Time: 0-15s**
- Show Streamlit app loading
- Navigate to http://localhost:8501
- Voiceover: "AI Photography Coach - a multi-agent system powered by Google Gemini"

**Time: 15-30s**
- Upload a sample photo (drag & drop)
- Show EXIF metadata appearing
- Highlight: Camera model, ISO, aperture, focal length
- Voiceover: "VisionAgent extracts EXIF metadata and analyzes composition in real-time"

**Time: 30-50s**
- Type in chat: "How can I improve composition?"
- Show response generating
- Highlight dynamic response mentioning specific issues
- Voiceover: "KnowledgeAgent provides context-aware coaching using Gemini 1.5 Flash"

**Time: 50-70s**
- Expand debug panel
- Show session state and agent traces
- Voiceover: "Production-grade observability tracks every agent call and performance metric"

**Time: 70-85s**
- Quick cut to terminal running `python3 demo_eval.py`
- Show evaluation report opening in browser
- Highlight LLM-as-Judge scores
- Voiceover: "Automated evaluation ensures consistent quality using LLM-as-Judge"

**Time: 85-90s**
- Show GitHub repository page
- Display README with architecture diagrams
- Voiceover: "Full source code and documentation available on GitHub"
- End screen: https://github.com/prasadt1/ai-photography-coach-agents.git

### Recording Tools
- **macOS:** QuickTime Player (File → New Screen Recording)
- **Alternative:** OBS Studio (free, more features)
- **Screen resolution:** 1920x1080 (Full HD)
- **Format:** MP4 (H.264)
- **Max file size:** Kaggle typically allows up to 100MB

### Video Recording Commands
```bash
# Start Streamlit app
cd /Users/prasadt1/ai-photography-coach-agents
python3 -m streamlit run agents_capstone/app_streamlit.py

# In another terminal, prepare evaluation (but don't run until recording)
cd /Users/prasadt1/ai-photography-coach-agents

# During recording:
# 1. Show app interface
# 2. Upload photo from: agents_capstone/test_photos/ (if available) or use any sample photo
# 3. Interact with chat
# 4. Show debug panel
# 5. Run: python3 demo_eval.py
# 6. Show report: open agents_capstone/reports/evaluation_report.html
```

---

## Photo Selection Tips

For best demonstration, use photos with:
1. **Good EXIF data** – DSLR/mirrorless cameras provide rich metadata
2. **Obvious composition issues** – Centered subject, tilted horizon, etc.
3. **Varied scenarios** – Portrait, landscape, or street photography
4. **High resolution** – 1920px+ width for clarity in screenshots

### Sample Photo Sources
- Your own photos from a DSLR/mirrorless camera
- Unsplash (free, high-quality, but may lack EXIF)
- Flickr with Creative Commons license (often has EXIF preserved)
- Test photos in `agents_capstone/test_photos/` (if created during development)

---

## Kaggle Submission Checklist

- [ ] 4 screenshots saved as PNG/JPG (high quality)
- [ ] Screenshots clearly show functionality (no blurry text)
- [ ] Optional video rendered and under 100MB
- [ ] Video has clear audio or text overlays
- [ ] All media demonstrates actual system (not mockups)
- [ ] Captions prepared for each image/video
- [ ] GitHub repository link confirmed: https://github.com/prasadt1/ai-photography-coach-agents.git
- [ ] Enhanced writeup finalized (1497 words)
- [ ] Submission before deadline: Dec 2, 2025 at 2:59 AM GMT+7

---

## Next Steps

1. **Take screenshots** following the guide above
2. **Record video** (optional but recommended for impact)
3. **Copy enhanced writeup** from `KAGGLE_WRITEUP_ENHANCED.md`
4. **Upload media** to Kaggle submission form
5. **Paste writeup** into text field
6. **Submit before deadline**

---

## Diagram PNG Export (Mermaid to Image for Kaggle)

If the Kaggle editor does not render Mermaid or relative image paths, export diagrams locally and upload PNGs directly in the editor:

### 1. Install Mermaid CLI
```bash
npm install -g @mermaid-js/mermaid-cli
```

### 2. Generate PNGs
```bash
cd /Users/prasadt1/ai-photography-coach-agents
mmdc -i diagrams/multi_agent_flow.mmd -o diagrams/multi_agent_flow.png -b transparent
mmdc -i diagrams/evaluation_pipeline.mmd -o diagrams/evaluation_pipeline.png -b transparent
```

### 3. High-Resolution (Optional)
```bash
mmdc -i diagrams/multi_agent_flow.mmd -o diagrams/multi_agent_flow@2x.png -b transparent -s 2
mmdc -i diagrams/evaluation_pipeline.mmd -o diagrams/evaluation_pipeline@2x.png -b transparent -s 2
```

### 4. Upload to Kaggle
- Open the Kaggle writeup editor
- Use the image upload button to add each PNG
- Replace markdown `![...](diagrams/...)` with the uploaded file links
- Add concise alt text: `![Multi-Agent System Flow](<uploaded_path>)`

### 5. Verify Rendering
- Check that both diagrams appear in preview
- Ensure no broken relative paths remain

### 6. (Optional) SVG Export
```bash
mmdc -i diagrams/multi_agent_flow.mmd -o diagrams/multi_agent_flow.svg
mmdc -i diagrams/evaluation_pipeline.mmd -o diagrams/evaluation_pipeline.svg
```
Use SVG if Kaggle accepts vector uploads; prefer PNG for universal support.

---

## Fallback Methods (If CLI Issues Occur)

If `npm` or `mmdc` cannot be installed, use one of these alternatives:

### 1. Online Mermaid Editor
- Go to https://mermaid.live
- Paste contents from `diagrams/multi_agent_flow.mmd` and `diagrams/evaluation_pipeline.mmd`
- Click Export → PNG (or SVG)
- Download and rename: `multi_agent_flow.png`, `evaluation_pipeline.png`

### 2. Kroki HTTP API (No Node Required)
```bash
curl -X POST -H "Content-Type: text/plain" \
  --data-binary @diagrams/multi_agent_flow.mmd \
  https://kroki.io/mermaid/png > diagrams/multi_agent_flow.png

curl -X POST -H "Content-Type: text/plain" \
  --data-binary @diagrams/evaluation_pipeline.mmd \
  https://kroki.io/mermaid/png > diagrams/evaluation_pipeline.png
```

### 3. Docker (No Global Node Install)
```bash
docker run --rm -v $PWD/diagrams:/data minlag/mermaid-cli \
  -i /data/multi_agent_flow.mmd -o /data/multi_agent_flow.png -b transparent

docker run --rm -v $PWD/diagrams:/data minlag/mermaid-cli \
  -i /data/evaluation_pipeline.mmd -o /data/evaluation_pipeline.png -b transparent
```

### 4. ASCII Backup (Already Prepared Earlier)
If image upload fails, you can paste the earlier ASCII versions into the Kaggle editor to ensure at least structural clarity.

---

Good luck with your submission! 🎉
