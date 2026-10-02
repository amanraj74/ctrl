# 🚀 QONEQTFORGE — THE PERFECT MASTER BLUEPRINT
## CTRL FREAK 2026 | Hack Driven | Winning Industry-Level Architecture

> **Mission:** Don't just use Qoneqt. Build technology for Qoneqt.
> **Our Solution (QoneqtForge):** A 100% automated, production-grade 12-stage pipeline that transforms a topic into a publish-ready Qoneqt Global Feed video. No shortcuts. Industry-grade.

---

## 🏗 1. SYSTEM ARCHITECTURE

QoneqtForge uses a highly resilient **Triple-Fallback Architecture** ensuring the pipeline never fails during a live demo or production load.

```text
[ Next.js Frontend ] ──▶ [ FastAPI Orchestrator ] ──▶ [ 12-Stage Video Worker ]
```

### The Tech Stack (100% Free / Open Source)
- **Frontend:** Next.js 14, Tailwind CSS, Server-Sent Events (SSE) for real-time logs.
- **Backend:** FastAPI, Python, SQLModel (SQLite).
- **Video Assembly:** Raw FFmpeg (no heavy wrappers, pure speed & precision).
- **Generative AI Routers:**
  - **LLM Engine:** Gemini 2.0 Flash ➔ Groq (Llama-3) ➔ Ollama (Local)
  - **Visuals:** Pollinations.ai (Flux) ➔ Cloudflare Workers AI ➔ Pexels
  - **Voice (TTS):** Edge-TTS (Word-level timings) ➔ Piper
  - **Captions (ASR):** faster-whisper

---

## ⚙️ 2. THE 12-STAGE PIPELINE

This is what makes QoneqtForge the "best of the best". We don't just generate a video; we orchestrate a studio-level production line.

| Stage | Action | Description |
|---|---|---|
| **1. Ingest** | Validates Topic | Cleans user input and sets up the job workspace. |
| **2. Research** | Fact Extraction | Pulls real facts to prevent LLM hallucination. |
| **3. Script** | AI Writing | Generates a hook-first, community-aware script. |
| **4. Scenes** | Storyboarding | Breaks the script into 4-6 second visual scenes. |
| **5. Critic** | Auto-Revision | AI evaluates the script (Hook, Clarity, Safety) before proceeding. |
| **6. Visuals** | Parallel Generation | Fires asynchronous requests to Pollinations/Cloudflare for images. |
| **7. Voice** | Neural TTS | Generates voiceover and exact word-level timestamp boundaries. |
| **8. Captions** | `.ass` Rendering | Creates SubStation Alpha karaoke-style subtitles. |
| **9. Music** | Audio Ducking | Selects background music and applies volume ducking under speech. |
| **10. Compose** | FFmpeg Rendering | Applies Ken Burns zoom effects, transitions, and overlays text. |
| **11. QA** | Probing | Automatically verifies video resolution, duration, and framerate. |
| **12. Export** | Packaging | Zips the `.mp4`, thumbnail, and metadata for the Qoneqt Feed. |

---

## 📂 3. FOLDER STRUCTURE

```
qoneqtforge/
├── frontend/                  # Next.js Application (Port 3000)
│   ├── src/app/page.tsx       # Main generation dashboard
│   ├── src/components/        # Form, Status, Player, History
│   └── src/lib/api.ts         # Connects to FastAPI backend
│
├── backend/                   # FastAPI Server (Port 8000)
│   ├── app/api/               # REST endpoints & SSE streaming
│   ├── app/core/llm_router.py # Triple-fallback LLM logic
│   ├── app/core/img_router.py # Triple-fallback Image logic
│   ├── app/worker.py          # The 12-Stage Pipeline executor
│   └── assets/                # Fonts, Music, and Watermarks
│
├── docker-compose.yml         # One-click deployment
└── PROJECT_STATUS.md          # Live AI context and tracker
```

---

## 🚀 4. WINNING STRATEGY FOR THE JUDGES

To win CTRL FREAK, we must demonstrate that this isn't a fragile script—it's a product.

1. **Demonstrate Resilience:** Disconnect the internet or provide a bad API key for the primary LLM to show the fallback router kicking in automatically.
2. **Show Real-Time Progress:** Open the Next.js dashboard and show the live Server-Sent Events (SSE) streaming logs for all 12 stages.
3. **Publish Quality:** Emphasize the `.ass` karaoke captions and Ken Burns motion effects. Standard AI videos are static; ours moves.
4. **Deploy & Ship:** Use the provided Dockerfile/docker-compose to show it deployed live.

---

## 🛠 5. WHAT NEEDS TO BE DONE NEXT?

If you are a developer or an AI taking over this project, refer to `PROJECT_STATUS.md`.
The architecture is 100% built. Next steps are strictly:
1. Adding API keys to `backend/.env`
2. Starting `docker-compose up`
3. Running an end-to-end test generation.
