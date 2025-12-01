# YouTube Video Script: AI Photography Coach
**Target Length:** 2.5-3 minutes  
**Format:** Screen recording + voiceover

---

## Opening (0:00-0:20) - 20 seconds

**Visual:** Show title card with project name and GitHub link

**Script:**
> "What if every aspiring photographer had access to a personal coach that could analyze their photos, understand their questions, and provide tailored guidance—all powered by AI agents?
>
> I built exactly that using Google's Gemini API and a multi-agent architecture. Let me show you how it works."

**On-screen text:** 
- "AI Photography Coach"
- "Multi-Agent System with Gemini"
- "github.com/prasadt1/ai-photography-coach-agents"

---

## Problem Statement (0:20-0:45) - 25 seconds

**Visual:** Quick montage of:
1. Generic photography tutorial screenshot
2. Forum post with slow responses
3. Expensive coaching service pricing

**Script:**
> "The problem is simple: Millions of people are learning photography, but they struggle to get personalized feedback. 
>
> Generic tutorials don't address their specific photos. Forums are slow and inconsistent. And professional coaches cost hundreds of dollars per session.
>
> What photographers really need is instant, contextual feedback that understands both their image AND their conversation history."

**On-screen text:**
- "❌ Generic tutorials"
- "❌ Slow forums"
- "❌ Expensive coaches"
- "✓ Need: Instant + Personalized + Contextual"

---

## Why Agents? (0:45-1:10) - 25 seconds

**Visual:** Show architecture diagram (multi_agent_flow.png)

**Script:**
> "This is why I chose a multi-agent architecture instead of a single LLM.
>
> The VisionAgent specializes in technical analysis—extracting EXIF data like ISO, aperture, and focal length, then detecting composition issues.
>
> The KnowledgeAgent, powered by Gemini 1.5 Flash, handles coaching—generating personalized advice that references the specific issues found in your photo.
>
> And the Orchestrator ties it all together—managing conversation history, coordinating the agents, and persisting sessions with SQLite so you can return to previous conversations."

**On-screen text:**
- "3 Specialized Agents"
- "VisionAgent → Technical Analysis"
- "KnowledgeAgent → Gemini-Powered Coaching"
- "Orchestrator → Session Management"

---

## Architecture Deep Dive (1:10-1:35) - 25 seconds

**Visual:** Code walkthrough or detailed architecture slide

**Script:**
> "Here's what makes it production-ready:
>
> First, every response from Gemini is dynamic—not templates. The LLM adapts to your specific question and photo.
>
> Second, I implemented context compaction. After six conversation turns, the system automatically summarizes history to prevent token overflow, enabling 50-plus turn conversations.
>
> Third, the memory layer uses an ADK-compatible adapter pattern. That means it's built to migrate from SQLite to Google Cloud seamlessly when I deploy to production."

**On-screen text:**
- "✓ Dynamic LLM responses"
- "✓ Context compaction (50+ turns)"
- "✓ ADK-ready architecture"

---

## Demo (1:35-2:15) - 40 seconds

**Visual:** Live Streamlit app demonstration

**Script:**
> "Let me show you a quick demo.
>
> [Upload photo] I drag and drop a photo into the Streamlit interface.
>
> [Show EXIF] Instantly, the Vision Agent extracts all the technical data—camera model, f/2.8 aperture, ISO 400.
>
> [Type question] I ask: 'How can I improve composition?'
>
> [Show response] Within three seconds, Gemini analyzes the photo and responds with specific advice—suggesting I move the subject to the rule of thirds, explaining why based on the detected issues.
>
> [Follow-up] I ask a follow-up: 'What about in low light?'
>
> [Contextual response] The system remembers our previous conversation and adapts the advice for low-light scenarios, referencing the ISO 400 from the EXIF data.
>
> [Show evaluation] And here's the kicker—I built an LLM-as-Judge evaluation framework. It scores responses on relevance, completeness, accuracy, and actionability. This system averages 8.6 out of 10 across all metrics."

**On-screen actions:**
1. Upload image → Show EXIF panel
2. Ask question → Show response  
3. Follow-up question → Show contextual response
4. Show evaluation report (HTML dashboard)

**On-screen text:**
- "Upload → Instant EXIF extraction"
- "Ask → Dynamic coaching (< 3s)"
- "Follow-up → Context-aware responses"
- "Evaluation: 8.6/10 average score"

---

## The Build (2:15-2:45) - 30 seconds

**Visual:** Quick code snippets or GitHub repo

**Script:**
> "I built this in five days:
>
> Day one, I architected the multi-agent system with clean separation of concerns.
>
> Day two, I integrated Gemini for both vision analysis and coaching, replacing my initial template-based responses with fully dynamic LLM generation.
>
> Day three, I added observability—structured logging, latency tracking, and a debug panel.
>
> Day four, I built the LLM-as-Judge evaluation framework using Gemini as an automated quality reviewer.
>
> And day five, I deployed with Docker, wrote comprehensive documentation, and prepared for cloud deployment with Google's Agent Development Kit.
>
> The code is fully commented, production-ready, and available on GitHub."

**On-screen text:**
- "5-Day Build"
- "Day 1: Architecture"
- "Day 2: Gemini Integration"
- "Day 3: Observability"
- "Day 4: Evaluation"
- "Day 5: Deployment"

---

## Closing (2:45-3:00) - 15 seconds

**Visual:** Show final architecture diagram and GitHub link

**Script:**
> "This project demonstrates how multi-agent systems with specialized AI models can solve real-world problems better than monolithic approaches.
>
> Check out the full code on GitHub—link in the description. Thanks for watching!"

**On-screen text:**
- "github.com/prasadt1/ai-photography-coach-agents"
- "⭐ Star the repo"
- "📂 Full code + documentation"
- "🚀 Deploy guide included"

---

## Video Recording Tips

### Technical Setup
- **Screen resolution:** 1920x1080 (1080p)
- **Recording software:** OBS Studio, Camtasia, or Loom
- **Audio:** Use external mic (Blue Yeti, Rode) for better quality
- **Cursor highlighting:** Enable for easier following

### Streamlit Demo Tips
1. **Pre-load the app** (don't show startup time)
2. **Use a high-quality test image** (good EXIF data)
3. **Practice the flow** (smooth drag-and-drop, no typos)
4. **Have backup screenshots** in case of network issues

### Post-Production
- **Add transitions** between sections (smooth fades)
- **Highlight key text** on diagrams (zoom or arrows)
- **Include captions** for technical terms
- **Add background music** (low volume, non-distracting)

### YouTube Optimization
- **Title:** "AI Photography Coach: Multi-Agent System with Gemini | Full Demo & Build Walkthrough"
- **Description:** Include GitHub link, tech stack, and timestamps
- **Tags:** AI agents, Gemini API, Google Cloud, photography, machine learning, Python, Streamlit
- **Thumbnail:** Architecture diagram + "Multi-Agent System" text

---

## Timestamps for Description

```
0:00 - Introduction
0:20 - Problem Statement
0:45 - Why Agents?
1:10 - Architecture Deep Dive
1:35 - Live Demo
2:15 - The Build (5-Day Timeline)
2:45 - Conclusion & GitHub Link
```

---

## Backup Slides (If Recording Fails)

Have these ready as fallbacks:
1. Architecture diagram (multi_agent_flow.png)
2. Evaluation dashboard (evaluation_report.html screenshot)
3. Code snippets (orchestrator.py key methods)
4. EXIF extraction example
5. Gemini API response example

---

## Estimated Timings Breakdown

| Section | Time | Word Count |
|---------|------|------------|
| Opening | 0:20 | ~50 words |
| Problem | 0:25 | ~60 words |
| Why Agents | 0:25 | ~70 words |
| Architecture | 0:25 | ~75 words |
| Demo | 0:40 | ~115 words |
| The Build | 0:30 | ~85 words |
| Closing | 0:15 | ~35 words |
| **Total** | **3:00** | **~490 words** |

Speaking pace: ~160 words/minute (natural, conversational pace)

---

Good luck with the recording! 🎥
