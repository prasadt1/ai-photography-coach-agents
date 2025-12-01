# Video Recording Guide: AI Photography Coach Demo

This guide will help you record a professional demo video for your Kaggle submission.

---

## Pre-Recording Checklist

### ✅ Software Setup

- [ ] **Screen recording software installed:**
  - **macOS:** QuickTime, ScreenFlow, or OBS Studio
  - **Recommended:** [OBS Studio](https://obsproject.com/) (free, cross-platform)
  
- [ ] **Audio setup:**
  - [ ] External microphone (if available)
  - [ ] Quiet recording environment
  - [ ] Audio test recording completed

- [ ] **Video editing software** (optional):
  - iMovie (macOS)
  - DaVinci Resolve (free, professional)
  - Camtasia (paid)

### ✅ Application Setup

- [ ] **Streamlit app running:**
  ```bash
  python3 -m streamlit run agents_capstone/app_streamlit.py
  ```
  
- [ ] **Test image prepared:**
  - [ ] High-quality JPEG with good EXIF data
  - [ ] Subject matter clear and interesting
  - [ ] File named something professional (e.g., `demo_photo.jpg`)

- [ ] **Browser setup:**
  - [ ] Chrome/Firefox with clean tabs
  - [ ] Zoom level at 100%
  - [ ] Developer tools closed
  - [ ] Bookmarks bar hidden (for clean recording)

### ✅ Visual Assets Ready

- [ ] **Diagrams exported:**
  - [ ] `diagrams/multi_agent_flow.png`
  - [ ] `diagrams/evaluation_pipeline.png`
  
- [ ] **Evaluation report generated:**
  ```bash
  python3 demo_eval.py
  ```
  - [ ] `reports/evaluation_report.html` exists
  - [ ] Open in browser tab (ready to show)

- [ ] **GitHub repo page open:**
  - [ ] `https://github.com/prasadt1/ai-photography-coach-agents`
  - [ ] README visible and polished

---

## Recording Setup

### Display Configuration

**Resolution:** 1920x1080 (1080p) or 1280x720 (720p minimum)

**Layout:**
```
┌─────────────────────────────────────┐
│  Title Card (0:00-0:05)             │
│  - Project name                      │
│  - GitHub link                       │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Problem Slides (0:05-0:30)         │
│  - Screenshots/images               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Architecture Diagram (0:30-1:00)   │
│  - multi_agent_flow.png             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Live Demo (1:00-2:00)              │
│  - Streamlit app                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Evaluation + Code (2:00-2:45)      │
│  - HTML report                       │
│  - GitHub repo                       │
└─────────────────────────────────────┘
```

### OBS Studio Settings

1. **Create scenes:**
   - **Scene 1:** Title card (static image)
   - **Scene 2:** Problem explanation (slides)
   - **Scene 3:** Architecture diagram (static image with zoom)
   - **Scene 4:** Streamlit app (browser window capture)
   - **Scene 5:** Evaluation report (browser window capture)
   - **Scene 6:** GitHub repo (browser window capture)

2. **Video settings:**
   - Resolution: 1920x1080
   - Frame rate: 30 FPS
   - Encoder: Hardware (H.264)
   - Quality: High

3. **Audio settings:**
   - Sample rate: 48 kHz
   - Bitrate: 160 kbps
   - Noise suppression: Enabled

---

## Recording Process

### Phase 1: Preparation (10 minutes)

1. **Close unnecessary apps** (reduce CPU load, prevent notifications)
2. **Do Not Disturb mode ON**
3. **Open all tabs/windows you'll show:**
   - Streamlit app (localhost:8501)
   - Evaluation report (reports/evaluation_report.html)
   - GitHub repo
   - Diagram images
4. **Test audio:** Record 30 seconds, verify quality
5. **Practice transitions** between screens

### Phase 2: Recording (15-20 minutes)

**Tip:** Record in segments, not one continuous take. Easier to fix mistakes!

#### Segment 1: Introduction (0:00-0:30)
- **Visual:** Title card
- **Script:** Read opening from VIDEO_SCRIPT.md
- **Duration:** 30 seconds
- **Record:** Start → Read script → Stop

#### Segment 2: Architecture (0:30-1:00)
- **Visual:** Show multi_agent_flow.png
- **Script:** Explain agent architecture
- **Actions:** 
  - Zoom into diagram sections
  - Highlight VisionAgent, KnowledgeAgent, Orchestrator
- **Duration:** 30 seconds
- **Record:** Start → Explain → Stop

#### Segment 3: Live Demo (1:00-2:00)
- **Visual:** Streamlit app
- **Script:** Walk through demo interaction
- **Actions:**
  1. Upload image (drag & drop)
  2. Show EXIF extraction
  3. Type question: "How can I improve composition?"
  4. Show response (wait for full generation)
  5. Ask follow-up: "What about in low light?"
  6. Show contextual response
- **Duration:** 60 seconds
- **Record:** Start → Demo → Stop

**💡 Demo Tips:**
- **Slow down** cursor movements (easier to follow)
- **Pause** after each action (let viewer absorb)
- **Narrate** what you're doing ("Now I'll upload a photo...")
- If something breaks, **stop and restart segment**

#### Segment 4: Evaluation & Code (2:00-2:45)
- **Visual:** Evaluation report HTML + GitHub
- **Script:** Show quality metrics and code
- **Actions:**
  - Open evaluation report
  - Highlight scores (8.6/10 average)
  - Switch to GitHub repo
  - Scroll through README
- **Duration:** 45 seconds
- **Record:** Start → Show → Stop

#### Segment 5: Closing (2:45-3:00)
- **Visual:** Back to GitHub or title card
- **Script:** Call to action
- **Duration:** 15 seconds
- **Record:** Start → Close → Stop

### Phase 3: Review (5 minutes)

- [ ] Watch full recording
- [ ] Check audio levels (consistent, no clipping)
- [ ] Verify screen is visible (no tiny text)
- [ ] Confirm timing (under 3 minutes total)
- [ ] Note any re-record needs

---

## Post-Production

### Editing Checklist

- [ ] **Trim dead space** at start/end of each segment
- [ ] **Add transitions** (0.5s fade between segments)
- [ ] **Normalize audio** (consistent volume)
- [ ] **Add on-screen text:**
  - Key bullet points
  - GitHub link
  - Technical terms
- [ ] **Add background music** (optional, low volume)
  - YouTube Audio Library: "Ambient" or "Electronic" genre
  - Volume: 10-15% (doesn't distract from voice)
- [ ] **Add captions/subtitles** (improves accessibility)

### Export Settings

**Format:** MP4 (H.264)
**Resolution:** 1920x1080 (1080p)
**Frame rate:** 30 FPS
**Bitrate:** 8-10 Mbps (video), 192 kbps (audio)
**File size target:** < 500 MB

---

## YouTube Upload

### Video Details

**Title:**
```
AI Photography Coach: Multi-Agent System with Gemini | Full Demo & Build Walkthrough
```

**Description:**
```
I built an AI-powered photography coaching system using Google's Gemini API and a multi-agent architecture. This video demonstrates the full system including live demo, evaluation results, and technical architecture.

🔗 GitHub Repository: https://github.com/prasadt1/ai-photography-coach-agents
📚 Full Documentation: See DEPLOYMENT.md and README.md
📊 Evaluation Scores: 8.6/10 average (Relevance, Completeness, Accuracy, Actionability)

⏱️ TIMESTAMPS:
0:00 - Introduction
0:20 - Problem Statement
0:45 - Why Multi-Agent Architecture?
1:10 - System Architecture Deep Dive
1:35 - Live Demo (Streamlit + Gemini)
2:15 - The Build (5-Day Timeline)
2:45 - Evaluation Results & Code Walkthrough

🛠️ TECH STACK:
- Google Gemini API (1.5 Flash for coaching, Vision for analysis)
- Python 3.11
- Streamlit (Web UI)
- SQLite (Session persistence)
- Docker (Containerization)
- Multi-agent orchestration pattern

✨ KEY FEATURES:
- Dynamic LLM-powered coaching (not templates)
- EXIF metadata extraction and analysis
- Context-aware multi-turn conversations
- LLM-as-Judge evaluation framework
- Production-ready with ADK compatibility
- Comprehensive observability and logging

💻 Technologies: #Python #Gemini #AI #Agents #GoogleCloud #Photography #MachineLearning #LLM

📝 For more details, check out the full writeup and code in the GitHub repository!
```

**Tags:**
```
AI agents, Gemini API, Google Cloud, photography, machine learning, Python, Streamlit, multi-agent system, LLM, computer vision, EXIF, AI coaching, Google AI, photography tutorial, tech demo, coding project
```

**Thumbnail:**
- Architecture diagram with bold text: "Multi-Agent System"
- Project title and Gemini logo
- Use bright, contrasting colors
- Resolution: 1280x720

**Category:** Science & Technology

**Playlist:** Create "AI Projects" or "Kaggle Submissions"

---

## Common Issues & Solutions

### Issue: Streamlit app is slow during demo

**Solution:**
- Pre-warm the app (run a test query before recording)
- Use cached responses if possible
- If lag happens, pause recording and restart that segment

### Issue: Screen text too small

**Solution:**
- Zoom browser to 125-150%
- Use Streamlit's wide mode
- Show only relevant sections (crop other content)

### Issue: Audio has background noise

**Solution:**
- Use noise reduction in post-production (Audacity is free)
- Re-record audio separately and sync (ADR - Automated Dialogue Replacement)
- Enable noise gate in OBS

### Issue: Demo breaks during recording

**Solution:**
- **Don't panic!** Stop recording
- Fix the issue
- Restart from that segment
- Edit together in post-production

### Issue: Video file too large

**Solution:**
- Reduce bitrate (8 Mbps → 5 Mbps)
- Compress with HandBrake (free tool)
- Target: < 500 MB for <3 min video

---

## Quality Checklist (Before Upload)

- [ ] Video length: 2:30-3:00 minutes
- [ ] Audio clear and professional
- [ ] No typos in on-screen text
- [ ] GitHub link visible and correct
- [ ] Demo shows key features smoothly
- [ ] Evaluation scores prominently displayed
- [ ] Closing has clear call-to-action
- [ ] File size < 500 MB
- [ ] Resolution 1080p minimum
- [ ] Title, description, tags complete
- [ ] Thumbnail created and uploaded

---

## Alternative: Quick Loom Recording

If short on time, use [Loom](https://www.loom.com/) for a simpler workflow:

1. Install Loom desktop app
2. Select "Screen + Camera" mode (or just screen)
3. Record in one take following VIDEO_SCRIPT.md
4. Loom auto-uploads to cloud
5. Share link or download MP4

**Pros:** Fast, no editing needed
**Cons:** Less polished, can't fix mistakes easily

---

## Final Tips

✅ **Practice makes perfect:** Do 1-2 dry runs before final recording
✅ **Energy matters:** Sound enthusiastic (it's contagious!)
✅ **Pace yourself:** Speak clearly, not too fast
✅ **Show, don't just tell:** Visuals > words
✅ **Have fun!** Your passion for the project will show

Good luck! 🎬 You've got this! 🚀
