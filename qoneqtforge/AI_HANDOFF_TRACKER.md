# 🤖 AI-TO-AI HANDOFF & PHASE TRACKER
> **FOR HUMAN DEVELOPERS:** Before you start working or when you are done working, tell your AI (Antigravity/LLM) to "Read the AI_HANDOFF_TRACKER.md file". 
> **FOR AI DEVELOPERS:** Read this file completely to understand the exact state of the project, what was just finished, and what phase to build next. Do not deviate from this plan.

---

## 🎯 THE MASTER GOAL
We are building **QoneqtForge**, a 12-stage automated pipeline that generates vertical videos using a 100% free tech stack (Gemini Flash, Pollinations, Edge-TTS, FFmpeg, Next.js, FastAPI).

**Strict Rules for AI:**
1. **No Shortcuts:** If a phase requires error handling or fallbacks, build them.
2. **100% Free Stack:** Never suggest OpenAI or paid services. Stick to Gemini, Pollinations, and Edge-TTS.
3. **Phase-by-Phase:** Only work on the "IN PROGRESS" phase. Do not jump ahead.

---

## 🚦 PROJECT STATE & PHASE TRACKER
*When a phase is completed, the AI must change `[ ]` to `[x]` and move the `📍 CURRENTLY HERE` marker.*

### 🛠 Phase 1: Core Setup & Scaffold
- [x] Create backend FastAPI folder structure.
- [x] Create frontend Next.js folder structure.
- [x] Setup `docker-compose.yml` and `Makefile`.
- [x] Configure `.env.example` with required variables.

### 🧠 Phase 2: AI Routers & Connections
- [x] Build `llm_router.py` (Gemini 2.0 Flash integration + JSON output).
- [x] Build `img_pollinations.py` (Connect to Pollinations.ai via URL encoding).
- [x] Build `tts_service.py` (Connect to Edge-TTS for neural voice).
- [x] *AI Note: Test each provider in isolation before moving to Phase 3.*

### ⚙️ Phase 3: The 12-Stage Worker (The Brains)
- [x] **Stages 1-3:** Ingest topic, fetch facts, generate Script.
- [x] **Stages 4-5:** Break into Scenes, pass through AI Critic.
- [x] **Stages 6-7:** Trigger parallel Image and Voice generation.
- [x] **Stage 8:** Generate SubStation Alpha (`.ass`) captions.
- [x] *AI Note: Save all artifacts (json, mp3, png) to `data/jobs/<id>/`.*

### 🎬 Phase 4: Video Composition (FFmpeg)
- [x] Build `compose.py`.
- [x] Add background music with audio ducking (lower music volume when speaking).
- [x] Apply Ken Burns zoom effects to images.
- [x] Render final MP4 in 9:16 portrait mode (1080x1920).

### 🖥 Phase 5: Next.js Frontend
- [x] Build Dashboard (Topic Input + Advanced Settings).
- [x] Build Job Details page (Real-time progress bar via SSE).
- [x] Build Video Player & Download button.

### 🚀 Phase 6: Final Polish & Deployment (📍 CURRENTLY HERE)
- [x] QA: Test edge cases (weird topics, API timeouts).
- [ ] Deploy Backend to Railway.app.
- [ ] Deploy Frontend to Vercel.

---

## 💬 LAST HANDOFF NOTES
**(Humans or AI should leave notes here before logging off)**

* **Date:** October 2, 2026
* **Completed by:** Antigravity (AI)
* **Message for Next Dev:** "I have successfully run end-to-end QA tests! Fixed three critical bugs: 1) Staggered image generation in `s06_visuals.py` to prevent Pollinations 402 Rate Limit errors. 2) Fixed a frontend SSE reconnection bug in `sse.ts` and `page.tsx` that prevented the UI from updating if the connection dropped. 3) Discovered that clicking inside the Windows Terminal pauses Uvicorn processes, so remember to press Esc if the backend hangs. Next up is deploying to Railway and Vercel!"

---
*AI Prompt: "I have read the handoff tracker. Let's finish Phase 6 deployment."*
