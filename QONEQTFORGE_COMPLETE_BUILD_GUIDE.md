# 🏆 QoneqtForge — Complete End-to-End Build Guide

> **Mission**: Build a production-grade, LLM-powered content pipeline that transforms topics/trends into publish-ready vertical (9:16) videos for the Qoneqt Global Feed — fully automated, self-critiquing, and 100% free to run.

> **Event**: CTRL FREAK 2026 · HackBriven · 8-hour offline hackathon · 4 Oct 2026 · York·IE, Ahmedabad

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [100% Free Tech Stack](#2-100-free-tech-stack)
3. [System Architecture](#3-system-architecture)
4. [Complete Folder & File Structure](#4-complete-folder--file-structure)
5. [Phase 1: Repository Scaffold](#5-phase-1-repository-scaffold)
6. [Phase 2: Core Infrastructure](#6-phase-2-core-infrastructure)
7. [Phase 3: Pipeline Stages 1-5 (Content Intelligence)](#7-phase-3-pipeline-stages-1-5)
8. [Phase 4: Pipeline Stages 6-9 (Media Generation)](#8-phase-4-pipeline-stages-6-9)
9. [Phase 5: Video Composition & QA](#9-phase-5-video-composition--qa)
10. [Phase 6: Backend API & Orchestration](#10-phase-6-backend-api--orchestration)
11. [Phase 7: Frontend (Next.js)](#11-phase-7-frontend-nextjs)
12. [Phase 8: Deployment & CI/CD](#12-phase-8-deployment--cicd)
13. [Phase 9: Documentation & Samples](#13-phase-9-documentation--samples)
14. [Phase 10: Hardening & Polish](#14-phase-10-hardening--polish)
15. [Environment Variables Reference](#15-environment-variables-reference)
16. [Key Design Decisions](#16-key-design-decisions)
17. [Hackathon Day Execution Timeline](#17-hackathon-day-execution-timeline)
18. [Win Strategy & Differentiators](#18-win-strategy--differentiators)

---

## 1. Project Overview

### What is QoneqtForge?

QoneqtForge is an **AI-powered content pipeline** that:

1. **Ingests** a topic, prompt, idea, or trending topic
2. **Researches** facts using LLM + web sources (no hallucination)
3. **Writes** a hook-first, community-aware script with retention beats
4. **Plans** visual scenes with cinematic prompts
5. **Self-critiques** via an LLM quality gate (auto-revises weak content)
6. **Generates** AI images + stock visuals with Ken Burns motion
7. **Synthesizes** neural voice narration (edge-tts, multi-language)
8. **Burns** word-level karaoke captions (ASS subtitles)
9. **Selects & ducks** royalty-free background music
10. **Composes** a professional 1080×1920 30fps video (FFmpeg + MoviePy)
11. **QA checks** the final video (resolution, loudness, black frames, etc.)
12. **Exports** a ready-to-publish pack (MP4 + thumbnail + caption + hashtags)

### Why Judges Will Love This

| Differentiator | Impact |
|---|---|
| **Qoneqt-native**: community-aware output, CTA drives to join/comment | Shows product understanding |
| **Multi-agent pipeline with Quality Gate**: LLM critic + rule checks | Reliable production workflow |
| **Batch / scale mode**: 1 trend list → N videos in a queue | "At scale", "repeatable" |
| **Trend ingestion**: RSS/Google Trends/Reddit/HN → ideas | Input = "trend" from brief |
| **Provider fallback chain**: Gemini → Groq → Ollama; Pollinations → CF → stock | Never fails on stage |
| **Observability**: per-stage logs, timings, cost = ₹0 dashboard | Engineering maturity |
| **Hook-first storytelling**: 3-sec hook, retention beats, burned captions | Real feed performance |

---

## 2. 100% Free Tech Stack

> [!IMPORTANT]
> Every single tool, service, and dependency used is **completely free**. Zero credit card required.

### Backend

| Component | Tool | Why Free |
|---|---|---|
| Runtime | Python 3.11+ | Open source |
| Framework | FastAPI + Uvicorn | Open source |
| Data Validation | Pydantic v2 | Open source |
| Database | SQLite via SQLModel | Built-in, no server |
| Queue | asyncio worker (in-process) | No Redis needed |
| Rate Limiting | slowapi | Open source |

### LLM Providers (Fallback Chain)

| Priority | Provider | Free Tier |
|---|---|---|
| 1st | Google Gemini API (gemini-2.0-flash) | AI Studio free tier — generous limits |
| 2nd | Groq (Llama 3.3 70B) | Free tier — very fast inference |
| 3rd | Ollama local (llama3.2:3b / qwen2.5:7b) | Fully local, unlimited |

### Image Generation (Fallback Chain)

| Priority | Provider | How |
|---|---|---|
| 1st | Pollinations.ai | No API key, direct URL |
| 2nd | Cloudflare Workers AI | Free tier (FLUX-1-schnell / SDXL) |
| 3rd | Hugging Face Inference API | Free tier |
| 4th | Pexels / Pixabay stock | Free API key |

### Voice & Audio

| Component | Tool | Cost |
|---|---|---|
| TTS | edge-tts (Microsoft neural voices) | Free, no key, Hindi/English/Gujarati |
| TTS Fallback | Piper TTS (offline) / pyttsx3 | Free |
| Captions/ASR | faster-whisper (local, tiny/base model) | Free |
| Music | Royalty-free MP3s from Pixabay Music | Free, pre-downloaded |

### Video

| Component | Tool | Cost |
|---|---|---|
| Composition | FFmpeg + MoviePy 2.x | Open source |
| Ken Burns | FFmpeg zoompan filter | Built-in |
| Captions | ASS subtitle format + libass | Built-in |

### Frontend

| Component | Tool | Cost |
|---|---|---|
| Framework | Next.js 14 (App Router) | Open source |
| Styling | Tailwind CSS | Open source |
| Components | shadcn/ui | Open source |
| Animations | Framer Motion | Open source |
| Icons | Lucide React | Open source |

### Deployment

| Component | Tool | Cost |
|---|---|---|
| Backend | Railway.app (Docker) | Free Tier ($5 credit, zero cost setup) |
| Frontend | Vercel | Free tier |
| CI/CD | GitHub Actions | Free for public repos |
| Storage | Local disk / Railway volume | Free |

### Development

| Tool | Purpose |
|---|---|
| Antigravity | AI pair-programmer (building all code) |
| Git + GitHub | Version control, public repo |
| Docker | Containerization |

---

## 3. System Architecture

```
┌────────────────────┐   ┌───────────────────────────────────────────────────────┐
│   Next.js Web UI   │   │                  FastAPI Backend                       │
│   (Vercel)         │──▶│  /api/jobs  /api/trends  /api/batch  /api/export      │
│                    │◀──│  /api/jobs/{id}/events (SSE live stream)               │
└────────────────────┘   │          │                                             │
                         │   ┌──────▼────── PIPELINE ORCHESTRATOR ──────────┐    │
                         │   │ 1 Ingest → 2 Research → 3 Script → 4 Scenes │    │
                         │   │ 5 Critic/Gate → 6 Visuals → 7 Voice         │    │
                         │   │ 8 Captions → 9 Music → 10 Compose           │    │
                         │   │ 11 QA → 12 Export Pack                      │    │
                         │   └─────────────────────────────────────────────┘    │
                         │                                                       │
                         │   Provider Layer (LLM / Image / TTS)                  │
                         │   ├── LLM Router: Gemini → Groq → Ollama             │
                         │   ├── Image Router: Pollinations → CF → Pexels       │
                         │   └── TTS Router: edge-tts → Piper → pyttsx3        │
                         │                                                       │
                         │   SQLite DB (jobs, stages, assets, logs)              │
                         │   /data/jobs/<id>/ (artifacts per job)                │
                         └───────────────────────────────────────────────────────┘
```

### Pipeline Flow (12 Stages)

```
┌─────────┐    ┌──────────┐    ┌────────┐    ┌───────────┐    ┌─────────────┐
│ 1.Ingest│───▶│2.Research │───▶│3.Script│───▶│4.ScenePlan│───▶│5.Critic/Gate│
└─────────┘    └──────────┘    └────────┘    └───────────┘    └──────┬──────┘
                                                                      │
                                         ┌────────────────────────────┘
                                         │ score < 7? → loop back to 3 (max 2x)
                                         ▼
┌─────────┐    ┌──────────┐    ┌────────┐    ┌───────────┐    ┌──────────┐
│6.Visuals│───▶│ 7.Voice  │───▶│8.Caption│──▶│ 9.Music   │───▶│10.Compose│
└─────────┘    └──────────┘    └────────┘    └───────────┘    └────┬─────┘
                                                                    │
                                                                    ▼
                                              ┌────────┐    ┌────────────┐
                                              │ 11.QA  │───▶│12.ExportPak│
                                              └────────┘    └────────────┘
```

---

## 4. Complete Folder & File Structure

> [!NOTE]
> This is the **exact** structure to generate. Every file listed here must be created.

```
c:\AntiGravity\CTRL\qoneqtforge\
├── README.md                           # Judges read this first (§14 of spec)
├── LICENSE                             # MIT License
├── .gitignore                          # Python, Node, .env, data/, etc.
├── .env.example                        # Template for all env vars
├── Makefile                            # make dev / test / lint / demo
├── docker-compose.yml                  # Local full stack (backend + frontend)
├── AGENTS.md                           # Rules for Antigravity agent
│
├── docs/
│   ├── ARCHITECTURE.md                 # Full system architecture doc
│   ├── DECISIONS.md                    # Every non-obvious design choice
│   ├── PROMPTS.md                      # All LLM prompts, versioned
│   ├── DEMO_SCRIPT.md                  # 3-min demo narration for judges
│   ├── PPT_OUTLINE.md                  # Round 2 PPT structure
│   └── images/
│       └── architecture.png            # Architecture diagram image
│
├── backend/
│   ├── Dockerfile                      # HF Spaces compatible (port 7860)
│   ├── requirements.txt                # All Python dependencies
│   ├── pyproject.toml                  # ruff + pytest config
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app, CORS, routers, startup worker
│   │   ├── config.py                   # pydantic-settings, reads .env
│   │   ├── db.py                       # SQLModel engine, session factory
│   │   ├── models.py                   # Job, StageRun, Asset, LogLine DB tables
│   │   ├── schemas.py                  # Pydantic: BriefSpec, Script, Scene, ScenePlan, QAReport
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py                 # POST /jobs, GET /jobs/{id}, SSE /jobs/{id}/events
│   │   │   ├── batch.py                # POST /batch (list of topics)
│   │   │   ├── trends.py              # GET /trends?source=hn|reddit|gtrends|rss
│   │   │   ├── export.py              # GET /jobs/{id}/export.zip
│   │   │   └── health.py              # GET /health — provider status check
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # Runs stages, resume, retries, timing, events
│   │   │   ├── worker.py              # asyncio queue + concurrency limit
│   │   │   ├── events.py             # SSE pub/sub per job
│   │   │   └── retry.py              # tenacity wrappers
│   │   │
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Abstract LLMProvider, ImageProvider, TTSProvider
│   │   │   ├── llm_gemini.py          # Google Gemini API provider
│   │   │   ├── llm_groq.py           # Groq API provider
│   │   │   ├── llm_ollama.py         # Ollama local provider
│   │   │   ├── llm_router.py         # Fallback chain + JSON-mode + repair
│   │   │   ├── img_pollinations.py   # Pollinations.ai image gen
│   │   │   ├── img_cloudflare.py     # Cloudflare Workers AI
│   │   │   ├── img_pexels.py         # Pexels stock photo/video
│   │   │   ├── img_router.py         # Image fallback chain
│   │   │   ├── tts_edge.py           # edge-tts Microsoft neural voices
│   │   │   ├── tts_piper.py          # Piper TTS offline fallback
│   │   │   └── asr_whisper.py        # faster-whisper for captions
│   │   │
│   │   ├── stages/
│   │   │   ├── __init__.py
│   │   │   ├── s01_ingest.py          # Topic/prompt → BriefSpec
│   │   │   ├── s02_research.py        # BriefSpec → facts list
│   │   │   ├── s03_script.py          # Facts → Script (hook, beats, CTA)
│   │   │   ├── s04_scenes.py          # Script → ScenePlan (N scenes)
│   │   │   ├── s05_critic.py          # Script+ScenePlan → CriticReport
│   │   │   ├── s06_visuals.py         # Scene prompts → images
│   │   │   ├── s07_voice.py           # Narration → WAV/MP3 + timings
│   │   │   ├── s08_captions.py        # Audio → word-level ASS subtitles
│   │   │   ├── s09_music.py           # Mood → track selection + ducking
│   │   │   ├── s10_compose.py         # Everything → final.mp4
│   │   │   ├── s11_qa.py              # final.mp4 → QA checks
│   │   │   └── s12_export.py          # → Export pack (MP4, thumbnail, caption, etc.)
│   │   │
│   │   ├── video/
│   │   │   ├── __init__.py
│   │   │   ├── kenburns.py            # zoom/pan variants (in, out, left, right)
│   │   │   ├── transitions.py        # crossfade, slide transitions
│   │   │   ├── captions_ass.py       # Build .ass with word highlight (karaoke)
│   │   │   ├── audio_mix.py          # Ducking + loudnorm
│   │   │   ├── overlays.py           # Hook text, watermark, end card
│   │   │   └── ffmpeg_utils.py       # FFmpeg command wrappers
│   │   │
│   │   ├── prompts/
│   │   │   ├── research.md            # Research stage prompt
│   │   │   ├── script.md              # Script generation prompt
│   │   │   ├── scenes.md              # Scene planning prompt
│   │   │   ├── critic.md              # Critic/quality gate prompt
│   │   │   └── community_profiles.yaml # 6-8 community profiles
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── json_repair.py         # Fix malformed JSON from LLMs
│   │       ├── safety.py             # Banned-topic filter, PII check
│   │       ├── text.py               # Text utilities
│   │       └── paths.py              # Path management utilities
│   │
│   ├── assets/
│   │   ├── music/                     # 8-10 royalty-free MP3 tracks
│   │   │   └── music.json            # Track metadata (mood, bpm, source, license)
│   │   ├── fonts/                     # Inter, Poppins, Noto Sans Devanagari, Noto Gujarati
│   │   └── brand/                     # watermark.png, endcard.png (our own design)
│   │
│   ├── data/                          # Runtime directory (gitignored)
│   │   └── .gitkeep
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Shared test fixtures
│       ├── test_schemas.py            # Schema validation tests
│       ├── test_json_repair.py        # JSON repair utility tests
│       ├── test_llm_router.py        # Mocked provider failure tests
│       ├── test_captions_ass.py      # Caption generation tests
│       ├── test_compose_smoke.py     # 2-scene video from fixtures
│       └── fixtures/
│           ├── sample_script.json
│           ├── sample_scene_plan.json
│           └── sample_image.png
│
├── frontend/
│   ├── package.json
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.ts             # Tailwind with custom theme
│   ├── tsconfig.json
│   ├── postcss.config.js
│   │
│   └── src/
│       ├── app/
│       │   ├── layout.tsx             # Root layout (dark theme, fonts)
│       │   ├── page.tsx               # Home page (hero + create form)
│       │   ├── globals.css            # Global styles
│       │   ├── jobs/
│       │   │   └── [id]/
│       │   │       └── page.tsx       # Live pipeline view + player + export
│       │   ├── batch/
│       │   │   └── page.tsx           # Batch mode
│       │   ├── gallery/
│       │   │   └── page.tsx           # Generated videos gallery
│       │   └── about/
│       │       └── page.tsx           # Architecture + how it fits Qoneqt
│       │
│       ├── components/
│       │   ├── BriefForm.tsx           # Topic input + options form
│       │   ├── TrendPicker.tsx        # Live trending topics chips
│       │   ├── PipelineTimeline.tsx   # 12 stages with live status + timings
│       │   ├── ScenePreview.tsx       # Editable scene cards (regenerate one scene)
│       │   ├── VideoPlayer.tsx        # 9:16 phone-frame video preview
│       │   ├── ExportPanel.tsx        # Download + copy caption + "Open Qoneqt"
│       │   ├── LogConsole.tsx         # Real-time log viewer
│       │   ├── Navbar.tsx             # Navigation bar
│       │   ├── Footer.tsx             # Footer with metrics
│       │   └── ui/                    # shadcn/ui components
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── input.tsx
│       │       ├── select.tsx
│       │       ├── badge.tsx
│       │       ├── progress.tsx
│       │       ├── dialog.tsx
│       │       ├── tabs.tsx
│       │       ├── toast.tsx
│       │       └── skeleton.tsx
│       │
│       └── lib/
│           ├── api.ts                 # API client functions
│           ├── sse.ts                 # Server-Sent Events handler
│           └── types.ts              # TypeScript type definitions
│
├── scripts/
│   ├── generate_sample.py             # CLI: python scripts/generate_sample.py "topic"
│   ├── batch_demo.py                  # Generate 5 videos from trends
│   ├── download_music.md              # Instructions for getting music tracks
│   └── prerender_demo.sh             # Safety-net pre-rendered videos
│
├── samples/                           # Committed example outputs (2-3 MP4s)
│   └── .gitkeep
│
└── .github/
    └── workflows/
        └── ci.yml                     # ruff + pytest + frontend build
```

**Total files to generate: ~100+**

---

## 5. Phase 1: Repository Scaffold

### What to do:
1. Create the entire folder structure from §4
2. Initialize every file (empty but valid — proper `__init__.py`, headers, etc.)
3. Set up `.gitignore`, `.env.example`, `Makefile`, `AGENTS.md`
4. Initialize git repository

### Key Files:

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*.so
.venv/
venv/
*.egg-info/
dist/
build/

# Environment
.env
.env.local

# Data (runtime generated)
backend/data/jobs/
backend/data/*.db

# Node
node_modules/
.next/
out/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Misc
*.log
```

#### `.env.example`
```env
# === LLM Providers ===
GEMINI_API_KEY=your_google_ai_studio_key_here
GROQ_API_KEY=your_groq_key_here
# OLLAMA_BASE_URL=http://localhost:11434  # Uncomment if using Ollama

# === Image Providers ===
# Pollinations needs no key
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
CLOUDFLARE_ACCOUNT_ID=your_cf_account_id
CLOUDFLARE_API_TOKEN=your_cf_api_token

# === App Config ===
MAX_CONCURRENT_JOBS=2
DEFAULT_LANGUAGE=en
DEFAULT_DURATION=30
DEFAULT_COMMUNITY=general

# === Deployment ===
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
DATABASE_URL=sqlite:///./data/qoneqtforge.db
```

#### `Makefile`
```makefile
.PHONY: dev test lint demo setup

setup:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	cd backend && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

test:
	cd backend && pytest -v
	cd frontend && npm run build

lint:
	cd backend && ruff check . && ruff format --check .

demo:
	cd backend && python -m scripts.generate_sample "AI is changing education"

docker:
	docker compose up --build
```

#### `AGENTS.md`
```markdown
# Agent Rules
1. Follow QONEQTFORGE_MASTER_SPEC.md exactly. Structure in §4 is mandatory.
2. Only free services. Never add paid dependencies or require credit cards.
3. Every provider call: timeout, retry, fallback, logging. No bare requests.
4. Every stage: idempotent, writes outputs to data/jobs/<id>/, emits SSE events.
5. Type hints everywhere, Pydantic validation at boundaries, ruff-clean.
6. Write a test for every util + a compose smoke test. Run tests before saying "done".
7. Secrets only via .env. Never print keys.
8. After each phase: run it, show the output file/screenshot, fix errors, then commit.
9. Keep docs/DECISIONS.md updated. Small, meaningful commits (conventional commits).
10. If unsure, choose the simplest reliable option and note it. Never silently stub: mark TODOs explicitly.
```

---

## 6. Phase 2: Core Infrastructure

### Files to implement:

#### `backend/app/config.py` — Configuration Management
- Use `pydantic-settings` to read `.env`
- Define all config fields with defaults
- Validate on startup
- Fields: all API keys, database URL, cors origins, max concurrent jobs, default language/community/tone

#### `backend/app/schemas.py` — Data Contracts (Critical!)
These are the exact Pydantic v2 models that the entire pipeline uses:

```python
# BriefSpec — input to the pipeline
class BriefSpec(BaseModel):
    topic: str
    source_type: Literal["topic","prompt","idea","trend"] = "topic"
    community: str = "general"
    tone: Literal["energetic","calm","funny","inspiring","explainer"] = "energetic"
    language: Literal["en","hi","gu"] = "en"
    duration_sec: Literal[20,30,45,60] = 30
    voice: str | None = None
    visual_style: str = "cinematic"

# Beat — a story beat in the script
class Beat(BaseModel):
    role: Literal["hook","context","insight","proof","cta"]
    text: str

# Script — the complete script
class Script(BaseModel):
    title: str
    hook: str            # <= 12 words
    beats: list[Beat]
    cta: str
    caption: str         # <= 300 chars for Qoneqt post
    hashtags: list[str]  # 5-8 hashtags
    facts_used: list[str]

# Scene — one visual scene
class Scene(BaseModel):
    idx: int
    narration: str
    on_screen_text: str | None  # <= 6 words
    visual_prompt: str
    visual_source: Literal["ai_image","stock"] = "ai_image"
    stock_query: str | None
    motion: Literal["zoom_in","zoom_out","pan_left","pan_right","tilt_up"]
    duration_sec: float

# ScenePlan — all scenes together
class ScenePlan(BaseModel):
    style_prefix: str  # shared visual consistency
    scenes: list[Scene]

# CriticReport — quality gate output
class CriticReport(BaseModel):
    scores: dict[str,int]  # hook, clarity, factuality, pacing, safety, community_fit
    overall: float
    issues: list[str]
    must_fix: list[str]
    pass_: bool
```

#### `backend/app/db.py` — Database Layer
- SQLModel engine with SQLite
- Session factory
- Auto-create tables on startup

#### `backend/app/models.py` — Database Tables
- `Job`: id, status, brief_spec JSON, created_at, updated_at, current_stage, error
- `StageRun`: id, job_id FK, stage_name, status, started_at, completed_at, duration_ms, output_json, error
- `Asset`: id, job_id FK, stage_name, asset_type, file_path, metadata_json
- `LogLine`: id, job_id FK, stage_name, level, message, timestamp

#### `backend/app/utils/json_repair.py` — JSON Repair
- Strip markdown fences (```json ... ```)
- Fix trailing commas
- Fix single quotes → double quotes
- Balance braces/brackets
- Use `json-repair` library as fallback
- Tests: `test_json_repair.py`

#### `backend/app/utils/safety.py` — Content Safety
- Banned topics list (violence, explicit, etc.)
- PII detection (emails, phone numbers)
- Content filter function

#### `backend/app/utils/text.py` — Text Utilities
- Word count
- Truncate to word boundary
- Clean whitespace
- Estimate speaking duration (words per minute)

#### `backend/app/utils/paths.py` — Path Management
- Job directory creation: `data/jobs/<id>/`
- Stage output paths
- Asset paths
- Temp file management

#### Provider Base Classes (`backend/app/providers/base.py`)
```python
class LLMProvider(ABC):
    @abstractmethod
    async def complete_json(self, prompt: str, schema: type[BaseModel], **kwargs) -> BaseModel: ...

class ImageProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, width: int, height: int, **kwargs) -> bytes: ...

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str, output_path: Path) -> dict: ...
    # Returns: {"audio_path": str, "word_timings": list[dict]}
```

#### LLM Providers
- `llm_gemini.py`: Google AI Studio API, `gemini-2.0-flash`, JSON mode, `response_mime_type=application/json`
- `llm_groq.py`: Groq API, Llama 3.3 70B, JSON mode
- `llm_ollama.py`: Local Ollama, any model, format JSON
- `llm_router.py`: The **fallback chain**:
  ```python
  CHAIN = [GeminiProvider, GroqProvider, OllamaProvider]
  async def complete_json(prompt, schema, **kw):
      for P in CHAIN:
          try:
              return await with_retry(P().complete_json, prompt, schema, attempts=2, backoff=1.5)
          except (RateLimit, Timeout, ValidationError) as e:
              log_provider_failure(P.__name__, e)
      raise PipelineError("all LLM providers failed")
  ```

#### Image Providers
- `img_pollinations.py`: `https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&seed={n}&nologo=true&model=flux`
- `img_cloudflare.py`: Cloudflare Workers AI (FLUX-1-schnell / SDXL)
- `img_pexels.py`: Pexels search API → download best match
- `img_router.py`: Pollinations (timeout 40s, 2 tries) → Cloudflare → Pexels stock

#### TTS Providers
- `tts_edge.py`: `edge-tts` with word-level timing data, multi-language support
- `tts_piper.py`: Offline Piper TTS fallback

#### ASR Provider
- `asr_whisper.py`: `faster-whisper` with `tiny`/`base` model, word-level timestamps

### Dependencies (`requirements.txt`)
```
# Core
fastapi>=0.110
uvicorn[standard]>=0.27
pydantic>=2.5
pydantic-settings>=2.1
sqlmodel>=0.0.14

# LLM
google-generativeai>=0.8
groq>=0.5

# Image
httpx>=0.27
aiohttp>=3.9

# TTS & ASR
edge-tts>=6.1
faster-whisper>=1.0

# Video
moviepy>=2.0
Pillow>=10.2

# Queue & Rate Limiting
slowapi>=0.1.9

# Utils
tenacity>=8.2
python-dotenv>=1.0
json-repair>=0.28

# Testing
pytest>=8.0
pytest-asyncio>=0.23
ruff>=0.3
```

---

## 7. Phase 3: Pipeline Stages 1-5 (Content Intelligence)

### Stage 1: Ingest (`s01_ingest.py`)
**Input**: Raw topic/prompt/URL + options  
**Output**: `BriefSpec` (validated)

Logic:
1. Parse input (could be a topic string, a URL, or a trend object)
2. Build `BriefSpec` with defaults from config
3. Create job directory: `data/jobs/<uuid>/`
4. Save `brief.json`
5. Emit SSE event: `stage_start: ingest`

### Stage 2: Research (`s02_research.py`)
**Input**: `BriefSpec`  
**Output**: `facts: list[str]` (grounded facts)

Logic:
1. Send topic to LLM with research prompt
2. Optionally fetch from Wikipedia API / RSS feeds for grounding
3. Extract 5-8 factual bullet points
4. Save `research.json`
5. These facts are the **only** source the script can use (prevents hallucination)

Research prompt (`prompts/research.md`):
```
SYSTEM: You are a research assistant. Given a TOPIC, produce 5-8 factual bullet points.
Each fact must be specific, verifiable, and interesting.
Include numbers, dates, or names where possible.
Do NOT make up statistics. If unsure, say "reportedly" or "approximately".
Format: JSON array of strings.
TOPIC: {topic}
```

### Stage 3: Script (`s03_script.py`)
**Input**: `BriefSpec` + `facts`  
**Output**: `Script` (validated)

Logic:
1. Load community profile from `community_profiles.yaml`
2. Calculate target word count from duration (~2.5 words/sec)
3. Send to LLM with script prompt
4. Validate with Pydantic
5. Check hook length (≤ 12 words)
6. Save `script.json`

### Stage 4: Scene Plan (`s04_scenes.py`)
**Input**: `Script` + `BriefSpec`  
**Output**: `ScenePlan` (validated)

Logic:
1. Calculate number of scenes (duration / avg 5 sec)
2. Send script to LLM with scene plan prompt
3. Validate: all narration text covers the full script
4. Validate: motions don't repeat consecutively
5. Validate: scene 1 is the most visually striking
6. Save `scene_plan.json`

### Stage 5: Critic / Quality Gate (`s05_critic.py`)
**Input**: `Script` + `ScenePlan` + `facts`  
**Output**: `CriticReport`

Logic:
1. Send script + scene plan + original facts to LLM critic
2. Score on 6 dimensions (1-10): hook, clarity, factuality, pacing, safety, community_fit
3. Calculate weighted overall score:
   - hook: 30%, clarity: 20%, factuality: 20%, pacing: 10%, safety: 10%, community_fit: 10%
4. `pass_ = overall >= 7.5 AND safety >= 8 AND factuality >= 8`
5. If fails: send `must_fix` issues back to script stage (max 2 revision loops)
6. Save `critic_report.json`
7. This is a **MAJOR judge-pleaser** — show before/after scores in UI

### CLI Test Script (`scripts/generate_sample.py`)
```python
# python scripts/generate_sample.py "AI is changing education"
# Runs stages 1-5, prints JSON output for each stage
```

---

## 8. Phase 4: Pipeline Stages 6-9 (Media Generation)

### Stage 6: Visuals (`s06_visuals.py`)
**Input**: `ScenePlan`  
**Output**: Images for each scene

Logic:
1. For each scene in parallel:
   a. Prepend `style_prefix` to `visual_prompt`
   b. Try image generation via `img_router`
   c. Resize/crop to exactly 1080×1920 (Pillow)
   d. Save as `scene_{idx}.png`
2. For stock scenes: search Pexels with `stock_query`
3. Log which provider served each scene (show in UI)
4. Never hard-fail — always return an image

### Stage 7: Voice (`s07_voice.py`)
**Input**: Full narration text (all scenes concatenated) or per-scene  
**Output**: WAV/MP3 audio + word-level timings

Logic:
1. For each scene:
   a. Synthesize narration via `edge-tts`
   b. Extract word-level timing boundaries (edge-tts provides these)
   c. Save `scene_{idx}_voice.mp3`
   d. Save `scene_{idx}_timings.json`
2. Calculate actual audio duration per scene (this overrides the plan's `duration_sec`)
3. Fallback: Piper TTS → pyttsx3

### Stage 8: Captions (`s08_captions.py`)
**Input**: Audio files + word timings  
**Output**: ASS subtitle file

Logic:
1. If edge-tts provided word timings → use directly
2. Else: run `faster-whisper` on audio for word-level timestamps
3. Generate ASS subtitle file with:
   - Word-by-word karaoke highlight (yellow active word)
   - Font: Poppins Bold 64-72px
   - White text, black outline 4px
   - Bottom-third safe zone (avoid top 250px / bottom 380px)
   - Hindi/Gujarati: use Noto Sans Devanagari / Noto Sans Gujarati fonts
4. Save `captions.ass`

### Stage 9: Music (`s09_music.py`)
**Input**: Script mood/tone  
**Output**: Selected & processed music track

Logic:
1. Read `assets/music/music.json` for track metadata
2. Match tone to track mood (energetic → upbeat, calm → ambient, etc.)
3. Trim track to video duration
4. Apply ducking: lower music -12dB under voice via `sidechaincompress`
5. Save `music_ducked.mp3`

---

## 9. Phase 5: Video Composition & QA

### Stage 10: Compose (`s10_compose.py`)
**Input**: All media from stages 6-9  
**Output**: `final.mp4` (1080×1920, 30fps)

This is the most complex stage. Detailed specs:

#### Video Specs
- Canvas: **1080×1920** (vertical 9:16)
- FPS: **30**
- Codec: `libx264 -crf 20 -preset medium -pix_fmt yuv420p`
- Audio: AAC 192k
- Flags: `-movflags +faststart`

#### Scene Processing
1. Each scene image upscaled to ≥1.25× canvas (so Ken Burns has room)
2. Ken Burns motion applied per scene's `motion` field:
   - `zoom_in`: slow zoom from wide to tight
   - `zoom_out`: slow zoom from tight to wide
   - `pan_left/right`: horizontal pan
   - `tilt_up`: vertical pan upward
3. Scene duration = **actual TTS audio length + 0.3s tail** (not the plan's guess)

#### Transitions
- 0.25s crossfade between scenes
- Vary: `fade`, `slideleft`

#### Hook Overlay
- First 2.5 seconds: large kinetic text animation of the hook
- Bold, eye-catching, draws viewer in

#### Captions
- Word-by-word highlighted ASS subtitles
- Bottom-third safe zone
- Font: Poppins Bold 64-72px
- Colors: white text, yellow active word, black outline 4px
- Safe zone: avoid top 250px and bottom 380px (feed UI overlays)

#### Audio Mix
1. Voice: normalized
2. Music: at -22 LUFS, ducked -12dB under voice (`sidechaincompress`)
3. Final: `loudnorm=I=-14:TP=-1.5:LRA=11`

#### End Card
- Last 1.5 seconds: "Join the conversation on Qoneqt"
- Our own CTA graphic (not official Qoneqt logo misuse)

#### Thumbnail
- Best frame from scene 1
- Title text overlay
- Save as `thumbnail.jpg`

### Stage 11: QA (`s11_qa.py`)
**Input**: `final.mp4`  
**Output**: `QAReport`

Rule-based checks (fail → flag or recompose):
- [ ] Resolution: 1080×1920 (ffprobe)
- [ ] Duration: within ±10% of target
- [ ] Audio stream present
- [ ] FPS: 30
- [ ] Loudness: -16 to -12 LUFS
- [ ] No black frames >0.5s (`blackdetect`)
- [ ] Caption coverage: ≥95% narration words in subtitles
- [ ] File size: ≤50MB
- [ ] Optional: sample 4 frames → Gemini vision → check for garbled text/NSFW

Output: `QAReport` with green/red checks — **shown in UI** (judge-pleaser!)

### Stage 12: Export Pack (`s12_export.py`)
**Input**: All pipeline outputs  
**Output**: Ready-to-publish ZIP

Files in export pack:
- `final.mp4` — the video
- `thumbnail.jpg` — thumbnail image
- `caption.txt` — Qoneqt post caption (≤300 chars)
- `hashtags.txt` — 5-8 hashtags
- `metadata.json` — full pipeline metadata
- `script.md` — human-readable script

---

## 10. Phase 6: Backend API & Orchestration

### Orchestrator (`core/orchestrator.py`)
The brain of the pipeline:
```python
async def run_pipeline(job_id: str, brief: BriefSpec):
    stages = [ingest, research, script, scenes, critic, visuals, voice, captions, music, compose, qa, export]
    for stage in stages:
        emit_event(job_id, "stage_start", stage.name)
        start = time.time()
        try:
            result = await stage.run(job_id, context)
            context[stage.name] = result
            duration_ms = (time.time() - start) * 1000
            save_stage_run(job_id, stage.name, "completed", duration_ms, result)
            emit_event(job_id, "stage_complete", {stage.name: result, "duration_ms": duration_ms})
        except Exception as e:
            save_stage_run(job_id, stage.name, "failed", error=str(e))
            emit_event(job_id, "stage_failed", {stage.name: str(e)})
            # Retry logic based on error type
```

### Worker (`core/worker.py`)
- asyncio queue with configurable concurrency limit (default: 2)
- Job submission → queued → processing → completed/failed
- Background worker started on app startup

### SSE Events (`core/events.py`)
- Per-job event pub/sub
- Frontend subscribes to `/api/jobs/{id}/events`
- Events: `stage_start`, `stage_complete`, `stage_failed`, `log`, `job_complete`
- Use `asyncio.Queue` per subscriber

### API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/jobs` | Create job from BriefSpec → returns job_id |
| `GET` | `/api/jobs/{id}` | Status, stages, assets, timing |
| `GET` | `/api/jobs/{id}/events` | SSE stream of live events |
| `POST` | `/api/jobs/{id}/scenes/{idx}/regenerate` | Redo one scene's visual |
| `POST` | `/api/jobs/{id}/recompose` | Recompose video after edits |
| `POST` | `/api/batch` | Multiple topics → N jobs |
| `GET` | `/api/trends?source=hn` | Trending topics from various sources |
| `GET` | `/api/jobs/{id}/export.zip` | Download export pack |
| `GET` | `/api/health` | Provider status + system health |

### Rate Limiting
- `slowapi`: 5 jobs/hour per IP
- Protects public demo from abuse

### Cleanup
- Jobs older than 24h auto-deleted (except `samples/`)

---

## 11. Phase 7: Frontend (Next.js)

### Design System
- **Theme**: Dark mode with Qoneqt-inspired purple accent (`#7C4DFF`)
- **Glass cards**: `backdrop-blur-lg bg-white/5 border border-white/10`
- **Animations**: Framer Motion for all transitions
- **Typography**: Inter for UI, Poppins for headings
- **Icons**: Lucide React

### Pages

#### Home Page (`page.tsx`)
- Hero section: "What should the world see today?"
- Big input field with glow effect
- Trending topics as interactive chips (live from API)
- Options drawer:
  - Community selector (tech, startup, fitness, etc.)
  - Tone picker (energetic, calm, funny, etc.)
  - Language (English, Hindi, Gujarati)
  - Duration (20s, 30s, 45s, 60s)
  - Visual style (cinematic, illustration, flat-vector, photoreal)
- "Generate" button with loading state

#### Job Page (`jobs/[id]/page.tsx`)
Three-column layout:
- **Left**: 12-stage pipeline timeline with live progress indicators + timing for each stage
- **Center**: Phone-frame (9:16) video player showing the final result
- **Right**: Tabbed panel:
  - Script tab: full script with hook highlighted
  - Scenes tab: editable scene cards with "Regenerate" button per scene
  - QA tab: quality report with green/red check indicators
  - Logs tab: real-time log console

#### Batch Page (`batch/page.tsx`)
- Textarea: paste 5+ topics (one per line)
- Or "Auto-pick 5 trends" button
- Grid of progress cards showing each job's status
- Link to gallery when done

#### Gallery Page (`gallery/page.tsx`)
- Grid of all generated videos
- Thumbnail + title + duration + creation time
- Click to view/play
- Download/export buttons

#### About Page (`about/page.tsx`)
- Architecture diagram
- How QoneqtForge fits Qoneqt
- Tech stack breakdown
- Team info

### Key Components

#### `BriefForm.tsx`
- Controlled form with all BriefSpec fields
- Form validation
- Submit → POST /api/jobs → redirect to job page

#### `TrendPicker.tsx`
- Fetches from `/api/trends`
- Interactive chips (click to auto-fill topic)
- Source tabs: HackerNews, Reddit, Google Trends

#### `PipelineTimeline.tsx`
- 12 stages listed vertically
- Status indicators: pending (gray) → running (blue pulse) → done (green) → failed (red)
- Duration shown for completed stages
- SSE-connected for live updates

#### `VideoPlayer.tsx`
- Phone frame mockup around a 9:16 video
- HTML5 video player with controls
- Placeholder while video is being generated

#### `ExportPanel.tsx`
- Download MP4 button
- Copy caption button
- Copy hashtags button
- "Open Qoneqt" external link
- "Posted ✅" checkbox

#### `LogConsole.tsx`
- Scrollable terminal-style log viewer
- Color-coded by level (info, warn, error)
- SSE-connected for live log streaming

### Footer Metrics
- "Cost per video: ₹0"
- "Avg render time: Xs"
- Pipeline stats

---

## 12. Phase 8: Deployment & CI/CD

### Backend → Hugging Face Spaces (Docker)

#### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

# Install FFmpeg with libass
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libass-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user (HF Spaces requirement)
RUN useradd -m -u 1000 appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Frontend → Vercel

#### `frontend/next.config.js`
```javascript
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}
```

### `docker-compose.yml` (Local Development)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:7860"
    env_file: .env
    volumes:
      - ./backend/data:/app/data
      - ./backend/assets:/app/assets

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### GitHub Actions CI (`.github/workflows/ci.yml`)
```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && ruff check .
      - run: cd backend && pytest -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
```

---

## 13. Phase 9: Documentation & Samples

### README.md Must Contain:
1. One-line pitch + GIF/screenshot
2. Live demo URL + demo video link + Qoneqt published video link
3. Problem → Solution (Qoneqt Global Feed at scale)
4. Architecture diagram + 12 stages table
5. Features (quality gate, fallbacks, batch, trends, export pack)
6. Tech stack (all free, ₹0/video)
7. Quick start (local), env vars table, `docker compose up`
8. Sample outputs (links to `samples/`)
9. Limitations & Roadmap
10. Team + License + AI-disclosure

### Demo Script (`docs/DEMO_SCRIPT.md`)
- **0:00–0:20**: Problem statement
- **0:20–0:50**: Pick a live trend → choose community → Generate
- **0:50–1:40**: Walk through script, quality gate catching & fixing
- **1:40–2:15**: Final video plays, QA report
- **2:15–2:40**: Batch mode: 5 videos queued
- **2:40–3:00**: Show video live on Qoneqt, cost ₹0, roadmap

### Generate 3 Sample Videos
Topics:
1. "AI is transforming education in India"
2. "Top 5 startup trends in 2026"
3. "Why mindfulness matters for developers"

---

## 14. Phase 10: Hardening & Polish

### Error Handling
- Every API endpoint: proper error responses (4xx, 5xx with detail)
- Every provider: timeout, retry, fallback, meaningful error messages
- UI: error states for all async operations
- UI: empty states (no videos yet, etc.)

### Performance
- Image generation: parallel per scene
- FFmpeg: `-threads 2` on free hosts
- Cleanup old jobs (>24h)
- `-preset veryfast` on free hosts if needed

### Accessibility
- Semantic HTML
- Keyboard navigation
- Screen reader labels
- Color contrast compliance

### Security
- Rate limiting
- Input sanitization
- No secrets in logs
- CORS properly configured

### Testing
- All utils: unit tests
- Provider router: mocked failure tests
- Compose: smoke test with 2-scene video
- API: integration tests
- Frontend: build test

---

## 15. Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google AI Studio API key |
| `GROQ_API_KEY` | Recommended | — | Groq API key |
| `PEXELS_API_KEY` | Recommended | — | Pexels stock photos key |
| `PIXABAY_API_KEY` | Optional | — | Pixabay stock photos key |
| `CLOUDFLARE_ACCOUNT_ID` | Optional | — | Cloudflare account ID |
| `CLOUDFLARE_API_TOKEN` | Optional | — | Cloudflare Workers AI token |
| `OLLAMA_BASE_URL` | Optional | `http://localhost:11434` | Ollama local URL |
| `MAX_CONCURRENT_JOBS` | No | `2` | Max parallel jobs |
| `DEFAULT_LANGUAGE` | No | `en` | Default language |
| `DEFAULT_DURATION` | No | `30` | Default video duration |
| `DEFAULT_COMMUNITY` | No | `general` | Default community |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins |
| `DATABASE_URL` | No | `sqlite:///./data/qoneqtforge.db` | Database URL |

### How to Get API Keys (All Free):

1. **Gemini**: Go to [AI Studio](https://aistudio.google.com/) → Get API key → Free tier
2. **Groq**: Go to [console.groq.com](https://console.groq.com/) → Sign up → API keys → Free tier
3. **Pexels**: Go to [pexels.com/api](https://www.pexels.com/api/) → Sign up → Get key → Free
4. **Pixabay**: Go to [pixabay.com/api/docs](https://pixabay.com/api/docs/) → Sign up → Get key → Free
5. **Cloudflare**: Sign up at [dash.cloudflare.com](https://dash.cloudflare.com/) → Workers AI → Free tier
6. **Hugging Face**: Sign up at [huggingface.co](https://huggingface.co/) → Settings → Access tokens → Free

---

## 16. Key Design Decisions

| Decision | Rationale |
|---|---|
| Image + Ken Burns instead of AI video models | GPU cost/latency/reliability; renders in ~60-120s on free CPU |
| SQLite instead of PostgreSQL | Zero setup, single file, perfect for hackathon |
| asyncio worker instead of Celery/Redis | No extra services, simpler, sufficient for demo |
| edge-tts instead of paid TTS | Free neural voices, multi-language, word timings |
| SSE instead of WebSocket | Simpler, one-directional (server→client), sufficient for progress |
| Next.js App Router | Latest React patterns, great DX, free Vercel deploy |
| Pydantic v2 strict schemas | Catch LLM output errors early, type safety |
| Fallback chains everywhere | Never fail on stage, impress judges with resilience |

---

## 17. Hackathon Day Execution Timeline

| Time | Goal | Output |
|---|---|---|
| 0:00–0:30 | Repo init, env, keys, install ffmpeg, spec to Antigravity | repo + AGENTS.md |
| 0:30–1:45 | Backend skeleton + schemas + LLM router + stages 1-5 | CLI makes script JSON |
| 1:45–3:00 | Image router + TTS + captions + compose (first video via CLI) | **First MP4** ✅ |
| 3:00–4:00 | Orchestrator, SQLite, SSE, API | API runs full job |
| 4:00–5:30 | Frontend (create, job page, player, export) | UI end-to-end |
| 5:30–6:15 | Deploy (HF Space + Vercel), test public URL | **Live URL** ✅ |
| 6:15–6:45 | Generate 3-5 real videos, publish 1 on Qoneqt | **Published** ✅ |
| 6:45–7:30 | Record demo video, polish README, screenshots | Demo + docs |
| 7:30–8:00 | Buffer, pre-rendered fallbacks, rehearse pitch | Ready ✅ |

> [!CAUTION]
> **Rule: Deploy by hour 6 at the latest.** A working simple app beats a perfect broken one. Commit every 30-45 min with meaningful messages.

---

## 18. Win Strategy & Differentiators

### What Sets Us Apart

1. **Not just "prompt → video"** — it's a full multi-agent pipeline with 12 stages
2. **Self-critiquing AI** — the quality gate catches weak hooks and auto-fixes them
3. **Community-aware** — output adapts to Qoneqt communities (tech, startup, fitness, etc.)
4. **Never fails** — triple-fallback on every provider (LLM, image, TTS)
5. **Batch mode** — 1 trend list → 5 videos, with progress tracking
6. **Trend ingestion** — auto-discovers what to create content about
7. **Observable** — every stage logged, timed, visible in UI
8. **₹0 cost** — entirely free stack, no credit card needed
9. **Production-quality video** — Ken Burns, karaoke captions, ducked music, loudnorm
10. **Export-ready** — MP4 + caption + hashtags in one ZIP, 30 seconds to publish

### Judge Q&A Preparation

| Question | Answer |
|---|---|
| "What if an API fails?" | Triple-fallback chains, health dashboard shows provider status |
| "How does it scale?" | Stateless stages, queue abstraction, swap SQLite→Postgres, horizontal workers |
| "How do you ensure quality?" | LLM critic gate, fact-grounding, safety filter, automated QA checks |
| "Why not AI video models?" | GPU cost/latency/reliability; our approach renders in ~60-120s on free CPU; pluggable provider exists |
| "What's novel?" | Community-aware + self-critiquing + QA'd + batch + trend loop — full production pipeline |

---

## Commands to Run (After Each Phase)

```bash
# Phase 1: Verify structure
tree qoneqtforge/

# Phase 2: Verify imports
cd qoneqtforge/backend && python -c "from app.schemas import BriefSpec; print('OK')"

# Phase 3: Test content pipeline
cd qoneqtforge && python scripts/generate_sample.py "AI in education"

# Phase 4: Test media generation
cd qoneqtforge && python -c "from app.providers.llm_router import complete_json; print('OK')"

# Phase 5: Generate first video
cd qoneqtforge && python scripts/generate_sample.py "Top startup trends" --full

# Phase 6: Start backend
cd qoneqtforge/backend && uvicorn app.main:app --reload --port 8000

# Phase 7: Start frontend
cd qoneqtforge/frontend && npm run dev

# Phase 8: Docker build
cd qoneqtforge && docker compose up --build

# Phase 9: Run all tests
cd qoneqtforge && make test

# Phase 10: Lint + final check
cd qoneqtforge && make lint && make test
```

---

> [!TIP]
> **For Antigravity Agent**: Execute this build guide phase by phase. Each phase is self-contained and testable. Don't skip ahead. Verify each phase works before moving to the next. The quality gate in Phase 3 and the video composition in Phase 5 are the two most complex parts — give them extra attention.

---

*Built with ❤️ for CTRL FREAK 2026 by HackBriven. Cost per video: ₹0. Quality: Industry-grade.*
