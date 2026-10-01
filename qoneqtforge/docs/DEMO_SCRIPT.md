# Demo Script (3 Minutes)

## For CTRL FREAK 2026 Finale Presentation

### 0:00–0:20 — The Problem
> "Every day, millions of creators struggle to produce quality video content consistently. For platforms like Qoneqt, the Global Feed needs fresh, engaging content at scale — but creating even one good short video takes hours. What if AI could do it in under 2 minutes?"

### 0:20–0:50 — Live Demo: Create a Video
> "Let me show you QoneqtForge in action."

1. Open the web app
2. Show trending topics loading from HackerNews/Reddit
3. Click a trend OR type a custom topic
4. Select community: "tech"
5. Choose tone: "energetic", language: "English", duration: 30s
6. Click "Generate" — show the pipeline timeline starting

### 0:50–1:40 — The Pipeline in Action
> "Watch the 12-stage pipeline work. First, it researches real facts — no hallucination. Then our AI writer crafts a hook-first script."

1. Point to the script with highlighted hook (≤ 12 words)
2. Show the Critic/Quality Gate catching a weak hook
3. Show before score (e.g., 6.2) → auto-revision → after score (8.1)
4. "This self-critiquing loop is what separates QoneqtForge from simple prompt-to-video tools"
5. Show images being generated, TTS voice being synthesized
6. Show "Provider: Pollinations.ai" badge on images

### 1:40–2:15 — The Result
> "And here's the final video."

1. Play the video in the phone-frame preview
2. Point out: Ken Burns motion, karaoke captions, background music
3. Show the QA Report — all green checks ✅
4. Show Export Panel: MP4, caption, hashtags ready

### 2:15–2:40 — Scale: Batch Mode
> "But one video isn't enough. Content at scale means batch production."

1. Switch to Batch page
2. Click "Auto-pick 5 trends"
3. Show 5 jobs queued and progressing
4. "5 videos, zero cost, fully automated"

### 2:40–3:00 — Live on Qoneqt + Closing
> "And this video? It's already live on the Qoneqt Global Feed."

1. Show the published video on Qoneqt
2. "Cost per video: ₹0. Render time: under 2 minutes."
3. "QoneqtForge: AI-powered content at scale, built for Qoneqt."
4. Show roadmap slide briefly
5. "Thank you!"

---

## Judge Q&A Preparation

| Likely Question | Answer |
|---|---|
| "What if an API fails?" | Triple-fallback chains on every provider. Show the health page with provider status. |
| "How does it scale?" | Stateless stages, queue abstraction, swap SQLite→Postgres, workers scale horizontally. |
| "How do you ensure quality/safety?" | Critic gate with 6-dimension scoring, fact-grounding prevents hallucination, safety filter, automated QA checks. |
| "Why not AI video models?" | GPU cost/latency/reliability. Our approach renders in ~60-120s on free CPU. We have a pluggable provider slot for future GPU models. |
| "What's novel?" | Community-aware + self-critiquing + QA'd + batch + trend ingestion. It's a full production pipeline, not a wrapper around an API. |
