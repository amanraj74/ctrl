# QoneqtForge — Master Build Spec (for Antigravity)

> **Antigravity: read this whole file before writing any code. Follow it in order. Do not skip phases. Do not invent paid services. Ask nothing unless blocked — make the best decision, note it in `docs/DECISIONS.md`.**

---

## 0. Mission

Build **QoneqtForge**: a repeatable, deployed, AI pipeline that turns a **topic / prompt / idea / trend** into a **publish-ready vertical (9:16) video** for the **Qoneqt Global Feed** (Qoneqt = community-first social platform: communities, creators, content, conversations).

Event: **CTRL FREAK 2026** (HackBriven), 8-hour offline finale, 4 Oct 2026, York·IE Ahmedabad.
Judging principle from the brief: **"We're not judging a concept. We're judging what you actually build and ship."**

### Deliverables (all mandatory)
1. Public GitHub repo (clean, documented, commits spread across the event)
2. Live deployment (public URL, works without login)
3. Demo video (≤ 3 min, screen recording + voiceover)
4. At least **one generated video published on Qoneqt Global Feed**

### What makes this win (differentiators — build these, not just "prompt → video")
| Differentiator | Why judges care |
|---|---|
| **Qoneqt-native**: community-aware output (pick a Qoneqt community/niche, tone adapts, CTA drives to join/comment) | Shows we understood the product |
| **Multi-agent pipeline with a Quality Gate** (LLM critic + rule checks; auto-regenerate weak scenes) | "Reliable production workflow" |
| **Batch / scale mode**: 1 trend list → N videos in a queue, with progress | Brief says "at scale", "repeatable" |
| **Trend ingestion** (free RSS/Google Trends/Reddit/HN) → ideas | Input = "trend" explicitly in brief |
| **Provider fallback chain** (Gemini → Groq → Ollama; Pollinations → Cloudflare → stock) | Never fails on stage |
| **Observability**: per-stage logs, timings, cost = ₹0 dashboard | Engineering maturity |
| **Hook-first storytelling** (3-sec hook, retention beats, captions burned-in) | Real feed performance |

---

## 1. Rules & Safety Before You Start

- **Check HackBriven rules**: many hackathons require the *project* to be built during the 8 hours. Prepare *accounts, API keys, this spec, and tooling* beforehand. Ask organizers whether pre-written boilerplate is allowed. If not, build everything on the day using this spec — it is designed to be buildable in 8h by an AI agent.
- **Free-tier limits change.** Verify each service's current free limits the day before. The architecture below has fallbacks so one dying provider never kills the demo.
- **Never commit secrets.** `.env` in `.gitignore`; only `.env.example` committed.
- **Content/licensing**: only use (a) AI-generated images, (b) Pexels/Pixabay stock (free license, attribute in metadata), (c) royalty-free music (Pixabay Music / YouTube Audio Library / self-generated). No copyrighted clips. No real-person likeness. Add "AI-generated" disclosure in the video description.
- **Qoneqt publishing**: there is no confirmed public upload API. Plan: generate the MP4 + caption + hashtags, then **upload via the Qoneqt app/web by hand**, and ask Qoneqt Team Support (they offer support during the hackathon) whether any upload API/format guidelines exist. Build an "Export Pack" (MP4 + caption.txt + hashtags) so publishing takes 30 seconds. If an API exists, add `publisher/qoneqt_api.py`.

---

## 2. 100% Free Tech Stack

| Layer | Primary (free) | Fallback (free) |
|---|---|---|
| **LLM (script, scene plan, critic)** | Google Gemini API free tier (`gemini-2.0-flash` or newest flash model — AI Studio key) | Groq free (Llama 3.3 70B) → Ollama local (`llama3.2:3b` / `qwen2.5:7b`) |
| **Image generation** | Pollinations.ai (no key, `https://image.pollinations.ai/prompt/...`) | Cloudflare Workers AI free (FLUX-1-schnell / SDXL), Hugging Face Inference free, then Pexels stock |
| **Stock video/photos** | Pexels API (free key) | Pixabay API (free key) |
| **Voice (TTS)** | `edge-tts` (Microsoft neural voices, free, no key; Hindi/English/Gujarati voices) | Piper TTS (offline), `pyttsx3` (last resort) |
| **Captions / timing** | `faster-whisper` (local, `tiny`/`base` model, word timestamps) | Estimate timings from TTS word boundaries (edge-tts gives them) |
| **Music** | Local royalty-free library in `assets/music/` (download 8–10 tracks from Pixabay Music beforehand) | Silence + SFX |
| **Video compose** | **FFmpeg** + **MoviePy 2.x** (Ken Burns zoom/pan, transitions, burned captions) | Pure FFmpeg filtergraph |
| **Backend** | **FastAPI** + Uvicorn + Pydantic v2 | — |
| **Queue / jobs** | In-process `asyncio` worker + SQLite (no Redis needed) | — |
| **DB** | SQLite via SQLModel | — |
| **Frontend** | **Next.js 14 (App Router) + Tailwind + shadcn/ui** | Plain React + Vite |
| **Trends** | Google Trends RSS, Hacker News API, Reddit `.json` (public), NewsAPI-free alternatives (RSS) | Manual topic list |
| **Deploy backend** | **Hugging Face Spaces (Docker, free CPU)** or Render free | Railway trial / local + ngrok/Cloudflare Tunnel |
| **Deploy frontend** | **Vercel free** | Cloudflare Pages |
| **Storage** | Local disk on Space + HF Dataset repo / Cloudflare R2 free tier | Return file directly |
| **CI** | GitHub Actions (free for public repos) | — |
| **Dev tool** | Antigravity (you), Git, GitHub | — |

> Video-generation models (Wan, LTX, etc.) need GPU. **Do not depend on them.** Our approach = *image generation + cinematic motion (Ken Burns) + stock b-roll + kinetic captions + voiceover*, which is exactly how top short-form feeds look and renders on free CPU. Optional bonus: a `providers/video_ai.py` plug-in for a free HF Space video model, behind a feature flag.

---

## 3. System Architecture

```
┌────────────┐   ┌────────────────────────────────────────────────────────────┐
│  Next.js   │   │                    FastAPI Backend                         │
│  Web UI    │──▶│  /api/jobs  /api/trends  /api/batch  /api/export           │
│ (Vercel)   │   │            │                                               │
└────────────┘   │     ┌──────▼───────  PIPELINE ORCHESTRATOR  ─────────┐     │
                 │     │ 1 Ingest → 2 Research → 3 Script → 4 Scenes    │     │
                 │     │ 5 Critic/Gate → 6 Visuals → 7 Voice → 8 Captions│    │
                 │     │ 9 Music → 10 Compose → 11 QA → 12 Export Pack  │     │
                 │     └──────────────────────────────────────────────────┘   │
                 │  Provider layer (LLM / Image / TTS) with fallback chains   │
                 │  SQLite (jobs, stages, assets, logs)  | /data/jobs/<id>/   │
                 └────────────────────────────────────────────────────────────┘
```

### Pipeline stages (each stage = idempotent, resumable, logged, timed)

| # | Stage | Input → Output | Notes |
|---|---|---|---|
| 1 | **Ingest** | topic/prompt/idea/trend URL + options → `BriefSpec` | Options: community, tone, language (en/hi/gu), duration 20/30/45/60s, voice |
| 2 | **Research** | BriefSpec → facts list | LLM + optional Wikipedia/RSS fetch; prevents hallucination; stores sources |
| 3 | **Script** | facts → `Script` (hook, beats, CTA, caption, hashtags) | Hook ≤ 12 words; 3 retention beats; community-aware CTA |
| 4 | **Scene plan** | Script → `ScenePlan` (N scenes: narration, on-screen text, visual prompt, motion type, duration) | Strict JSON schema |
| 5 | **Critic / Quality Gate** | Script+ScenePlan → score + fixes | Rubric: hook strength, clarity, factuality, pacing, safety, community fit. Score < 7/10 → auto-revise (max 2 loops) |
| 6 | **Visuals** | each scene → image (or stock clip) | Parallel; style-consistency prefix; retries + fallback; resize/crop to 1080×1920 |
| 7 | **Voice** | narration → WAV/MP3 + word timings | edge-tts |
| 8 | **Captions** | audio → word-level ASS subtitles (karaoke highlight) | faster-whisper or edge-tts boundaries |
| 9 | **Music** | mood → track chosen + ducked under voice | FFmpeg `sidechaincompress` |
| 10 | **Compose** | everything → `final.mp4` 1080×1920, 30fps, H.264/AAC | Ken Burns, crossfades, logo watermark, intro hook text, end card |
| 11 | **Video QA** | final.mp4 → checks | ffprobe: resolution, duration, audio present, loudness (EBU R128 normalize), no black frames; sample frames → LLM vision check (optional) |
| 12 | **Export Pack** | → `final.mp4`, `thumbnail.jpg`, `caption.txt`, `hashtags.txt`, `metadata.json`, `script.md` | Ready to upload to Qoneqt |

---

## 4. Repository Structure (generate exactly this)

```
qoneqtforge/
├── README.md                      # judges read this first (see §14)
├── LICENSE                        # MIT
├── .gitignore
├── .env.example
├── Makefile                       # make dev / test / lint / demo
├── docker-compose.yml             # local full stack
├── AGENTS.md                      # rules for Antigravity (copy §16)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md               # every non-obvious choice
│   ├── PROMPTS.md                 # all prompts, versioned
│   ├── DEMO_SCRIPT.md             # 3-min demo narration
│   ├── PPT_OUTLINE.md
│   └── images/architecture.png
├── backend/
│   ├── Dockerfile                 # HF Spaces compatible (port 7860)
│   ├── requirements.txt
│   ├── pyproject.toml             # ruff + pytest config
│   ├── app/
│   │   ├── main.py                # FastAPI app, CORS, routers, startup worker
│   │   ├── config.py              # pydantic-settings, reads .env
│   │   ├── db.py                  # SQLModel engine, session
│   │   ├── models.py              # Job, StageRun, Asset, LogLine tables
│   │   ├── schemas.py             # Pydantic: BriefSpec, Script, Scene, ScenePlan, QAReport
│   │   ├── api/
│   │   │   ├── jobs.py            # POST /jobs, GET /jobs/{id}, SSE /jobs/{id}/events
│   │   │   ├── batch.py           # POST /batch (list of topics)
│   │   │   ├── trends.py          # GET /trends?source=hn|reddit|gtrends|rss
│   │   │   ├── export.py          # GET /jobs/{id}/export.zip
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── orchestrator.py    # runs stages, resume, retries, timing, events
│   │   │   ├── worker.py          # asyncio queue + concurrency limit
│   │   │   ├── events.py          # SSE pub/sub per job
│   │   │   └── retry.py           # tenacity wrappers
│   │   ├── providers/
│   │   │   ├── base.py            # abstract LLMProvider, ImageProvider, TTSProvider
│   │   │   ├── llm_gemini.py
│   │   │   ├── llm_groq.py
│   │   │   ├── llm_ollama.py
│   │   │   ├── llm_router.py      # fallback chain + JSON-mode + repair
│   │   │   ├── img_pollinations.py
│   │   │   ├── img_cloudflare.py
│   │   │   ├── img_pexels.py      # stock photo/video fallback
│   │   │   ├── img_router.py
│   │   │   ├── tts_edge.py
│   │   │   ├── tts_piper.py
│   │   │   └── asr_whisper.py
│   │   ├── stages/
│   │   │   ├── s01_ingest.py
│   │   │   ├── s02_research.py
│   │   │   ├── s03_script.py
│   │   │   ├── s04_scenes.py
│   │   │   ├── s05_critic.py
│   │   │   ├── s06_visuals.py
│   │   │   ├── s07_voice.py
│   │   │   ├── s08_captions.py
│   │   │   ├── s09_music.py
│   │   │   ├── s10_compose.py
│   │   │   ├── s11_qa.py
│   │   │   └── s12_export.py
│   │   ├── video/
│   │   │   ├── kenburns.py        # zoom/pan variants (in, out, left, right)
│   │   │   ├── transitions.py     # crossfade, slide
│   │   │   ├── captions_ass.py    # build .ass with word highlight
│   │   │   ├── audio_mix.py       # ducking + loudnorm
│   │   │   ├── overlays.py        # hook text, watermark, end card
│   │   │   └── ffmpeg_utils.py
│   │   ├── prompts/
│   │   │   ├── research.md
│   │   │   ├── script.md
│   │   │   ├── scenes.md
│   │   │   ├── critic.md
│   │   │   └── community_profiles.yaml
│   │   └── utils/
│   │       ├── json_repair.py
│   │       ├── safety.py          # banned-topic filter, PII check
│   │       ├── text.py
│   │       └── paths.py
│   ├── assets/
│   │   ├── music/                 # 8–10 royalty-free mp3 + music.json (mood, bpm, source)
│   │   ├── fonts/                 # Inter / Poppins / Noto Sans Devanagari+Gujarati (OFL)
│   │   └── brand/                 # qoneqt-style watermark.png (our own, not their trademark misuse), endcard.png
│   ├── data/                      # runtime (gitignored): jobs/<id>/...
│   └── tests/
│       ├── test_schemas.py
│       ├── test_json_repair.py
│       ├── test_llm_router.py     # mocks provider failures
│       ├── test_captions_ass.py
│       ├── test_compose_smoke.py  # renders 2-scene video from fixtures
│       └── fixtures/
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx           # Create (hero + form)
│       │   ├── jobs/[id]/page.tsx # live pipeline view + player + export
│       │   ├── batch/page.tsx     # batch mode
│       │   ├── gallery/page.tsx   # generated videos
│       │   └── about/page.tsx     # architecture + how it fits Qoneqt
│       ├── components/
│       │   ├── BriefForm.tsx
│       │   ├── TrendPicker.tsx
│       │   ├── PipelineTimeline.tsx   # 12 stages w/ live status + timings
│       │   ├── ScenePreview.tsx       # editable scene cards (regenerate one scene)
│       │   ├── VideoPlayer.tsx        # 9:16 phone-frame preview
│       │   ├── ExportPanel.tsx        # download + copy caption + "Open Qoneqt"
│       │   └── LogConsole.tsx
│       └── lib/api.ts, sse.ts, types.ts
├── scripts/
│   ├── generate_sample.py         # CLI: python scripts/generate_sample.py "topic"
│   ├── batch_demo.py              # generate 5 videos from trends
│   ├── download_music.md          # how to get tracks
│   └── prerender_demo.sh          # safety-net videos for stage
├── samples/                       # committed example outputs (2–3 mp4s ≤ 15MB each + captions)
└── .github/workflows/ci.yml       # ruff + pytest + frontend build
```

---

## 5. Core Data Contracts (`schemas.py`)

```python
class BriefSpec(BaseModel):
    topic: str
    source_type: Literal["topic","prompt","idea","trend"] = "topic"
    community: str = "general"         # key from community_profiles.yaml
    tone: Literal["energetic","calm","funny","inspiring","explainer"] = "energetic"
    language: Literal["en","hi","gu"] = "en"
    duration_sec: Literal[20,30,45,60] = 30
    voice: str | None = None           # e.g. en-IN-NeerjaNeural
    visual_style: str = "cinematic"    # cinematic|illustration|flat-vector|photoreal

class Beat(BaseModel):
    role: Literal["hook","context","insight","proof","cta"]
    text: str

class Script(BaseModel):
    title: str
    hook: str                          # <= 12 words
    beats: list[Beat]
    cta: str
    caption: str                       # for Qoneqt post, <= 300 chars
    hashtags: list[str]                # 5-8
    facts_used: list[str]

class Scene(BaseModel):
    idx: int
    narration: str
    on_screen_text: str | None         # <= 6 words
    visual_prompt: str                 # image-gen prompt
    visual_source: Literal["ai_image","stock"] = "ai_image"
    stock_query: str | None
    motion: Literal["zoom_in","zoom_out","pan_left","pan_right","tilt_up"]
    duration_sec: float

class ScenePlan(BaseModel):
    style_prefix: str                  # shared across all prompts for consistency
    scenes: list[Scene]

class CriticReport(BaseModel):
    scores: dict[str,int]              # hook, clarity, factuality, pacing, safety, community_fit (1-10)
    overall: float
    issues: list[str]
    must_fix: list[str]
    pass_: bool
```

---

## 6. Prompts (store in `app/prompts/*.md`, version in `docs/PROMPTS.md`)

### 6.1 Script prompt (core)
```
SYSTEM: You are a senior short-form video writer for Qoneqt, a community-first social platform.
Write for a vertical feed where viewers decide in 2 seconds.
RULES:
- Hook <= 12 words, creates curiosity or a bold claim. No "Did you know".
- Structure: hook -> context -> 2 insights -> proof/example -> CTA.
- Spoken style, short sentences (<= 14 words), no jargon unless community requires.
- Use ONLY facts from FACTS. Never invent statistics.
- CTA invites interaction inside Qoneqt (comment, join the community, share).
- Language: {language}. Tone: {tone}. Community: {community_profile}. Target duration: {duration} sec (~{words} words).
OUTPUT: JSON matching the Script schema. No markdown.
```
### 6.2 Scene plan prompt
```
Convert SCRIPT into {n} scenes (avg 4-6 sec). For each scene return narration (verbatim slice of script),
on_screen_text (<=6 words, punchy), visual_prompt (concrete, vertical 9:16 composition, subject, lighting, camera,
NO text in image, NO real people/logos), motion (vary; never same twice in a row), duration_sec.
Also return ONE style_prefix (e.g. "cinematic, volumetric light, teal-orange grade, 35mm, ultra detailed") that keeps
visuals consistent. Scene 1 must be the most visually striking (hook).
```
### 6.3 Critic prompt
```
You are a strict viral-content editor. Score 1-10: hook, clarity, factuality (vs FACTS), pacing, safety, community_fit.
List issues and must_fix. overall = weighted mean (hook 30%, clarity 20%, factuality 20%, pacing 10%, safety 10%, community_fit 10%).
pass_ = overall >= 7.5 and safety >= 8 and factuality >= 8.
```
### 6.4 Community profiles (`community_profiles.yaml`)
Define 6–8 e.g. `tech`, `startup`, `fitness`, `finance-basics`, `travel`, `education`, `gaming`, `general` → each has `audience`, `tone_notes`, `cta_style`, `hashtag_seeds`, `taboo`. (Also write a note: "profiles are our assumption of Qoneqt communities; adjust after viewing the real feed.")

### 6.5 JSON reliability
Always: JSON mode/`response_mime_type=application/json` where supported → parse → on failure run `json_repair` → on failure ask LLM "fix this JSON" once → on failure fall to next provider. Validate with Pydantic; failing validation counts as failure.

---

## 7. Provider Layer — Fallback Logic

`llm_router.py`:
```python
CHAIN = [GeminiProvider, GroqProvider, OllamaProvider]   # order from env LLM_CHAIN
async def complete_json(prompt, schema, **kw):
    last = None
    for P in CHAIN:
        try:
            return await with_retry(P().complete_json, prompt, schema, attempts=2, backoff=1.5)
        except (RateLimit, Timeout, ValidationError) as e:
            log_provider_failure(P.__name__, e); last = e
    raise PipelineError("all LLM providers failed") from last
```
`img_router.py`: Pollinations (timeout 40s, 2 tries, vary `seed`) → Cloudflare → Pexels stock using `stock_query`. Always return an image; the pipeline must **never** hard-fail on a single scene. Log which provider served each scene (show in UI).

Pollinations URL pattern: `https://image.pollinations.ai/prompt/{urlencoded}?width=1080&height=1920&seed={n}&nologo=true&model=flux` (verify current params on day-of).

---

## 8. Video Composition Details (`s10_compose.py`)

- Canvas **1080×1920**, 30 fps, `libx264 -crf 20 -preset medium -pix_fmt yuv420p`, AAC 192k, `-movflags +faststart`.
- Each scene image upscaled to ≥1.25× canvas so Ken Burns has room; use FFmpeg `zoompan` or MoviePy `resized(lambda t: ...)` + crop.
- Scene durations **driven by actual TTS audio length** (+0.3s tail), not the plan guess.
- Transitions: 0.25s crossfade (`xfade`), vary between `fade`, `slideleft`.
- **Hook overlay**: first 2.5s large kinetic text of `hook` (or scene-1 `on_screen_text`).
- **Captions**: word-by-word highlighted ASS, bottom-third safe zone (keep out of top 250px / bottom 380px — feed UI overlays), font Poppins Bold 64–72px, white with yellow active word, black outline 4px. Devanagari/Gujarati use Noto fonts.
- **Audio**: voice normalized; music at −22 LUFS ducked −12 dB under voice via `sidechaincompress`; final `loudnorm=I=-14:TP=-1.5:LRA=11`.
- **End card** (1.5s): "Join the conversation on Qoneqt" + our own CTA graphic (no official logo misuse — use text/own mark unless Qoneqt Team permits their logo).
- **Thumbnail**: best frame from scene 1 + title text.

---

## 9. Video QA (`s11_qa.py`) — rule checks (fail → recompose or flag)

- ffprobe: 1080×1920, duration within ±10% of target, audio stream present, fps 30
- Loudness within −16..−12 LUFS
- Black-frame detection (`blackdetect`) none > 0.5s
- Caption coverage: ≥ 95% narration words appear in subtitles
- File size ≤ 50 MB (typical upload limit; confirm with Qoneqt)
- Optional: sample 4 frames → Gemini vision → "any garbled text, NSFW, distorted faces?" → flag

Output `QAReport` shown in UI with green/red checks. **This is a judge-pleaser.**

---

## 10. Backend API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/jobs` | create job from BriefSpec → returns `job_id` |
| GET | `/api/jobs/{id}` | status, stages, assets |
| GET | `/api/jobs/{id}/events` | **SSE** stream of stage events/logs |
| POST | `/api/jobs/{id}/scenes/{idx}/regenerate` | redo one scene's visual |
| POST | `/api/jobs/{id}/recompose` | recompose after edits |
| POST | `/api/batch` | `{topics:[...], options}` → N jobs |
| GET | `/api/trends?source=hn` | trending ideas |
| GET | `/api/jobs/{id}/export.zip` | export pack |
| GET | `/api/health` | provider status |

Concurrency: max 2 jobs at once (free CPU). Per-IP rate limit (e.g., 5 jobs/hour) via `slowapi` so the public demo isn't abused. Cleanup of jobs older than 24h except `samples/`.

---

## 11. Frontend UX (make it look premium)

- Dark theme with Qoneqt-like purple accent (`#7C4DFF`-ish), glass cards, smooth Framer Motion.
- **Home**: big input "What should the world see today?" + trend chips (live) + options drawer (community, tone, language, duration, style).
- **Job page**: left = 12-stage timeline w/ live progress + timings; center = phone-frame (9:16) player; right = script, scenes (editable, "regenerate scene"), QA report, logs.
- **Batch page**: paste 5 topics or "Auto-pick 5 trends" → grid of progress cards → gallery.
- **Export panel**: Download MP4, copy caption, copy hashtags, "Open Qoneqt" button, checklist "Posted ✅".
- Footer metric: "Cost per video: ₹0 · Avg render time: Xs".

---

## 12. 8-Hour Execution Plan (finale day)

| Time | Goal | Output |
|---|---|---|
| 0:00–0:30 | Repo init, env, keys, install ffmpeg, this spec to Antigravity | repo + `AGENTS.md` |
| 0:30–1:45 | Backend skeleton + schemas + LLM router + script/scene/critic stages | CLI makes script JSON |
| 1:45–3:00 | Image router + TTS + captions + compose (first end-to-end video via CLI) | **first MP4** — milestone 1 |
| 3:00–4:00 | Orchestrator, SQLite, SSE, API | API runs full job |
| 4:00–5:30 | Frontend (create, job page, player, export) | UI end-to-end |
| 5:30–6:15 | Deploy (HF Space + Vercel), test public URL | **live URL** — milestone 2 |
| 6:15–6:45 | Generate 3–5 real videos, **publish 1 on Qoneqt** | **published** — milestone 3 |
| 6:45–7:30 | Record demo video, polish README, screenshots | demo + docs |
| 7:30–8:00 | Buffer, pre-rendered fallbacks, rehearse pitch | ready |

**Rule: deploy by hour 6 at the latest. A working simple app beats a perfect broken one.** Commit every 30–45 min with meaningful messages.

---

## 13. Pre-Event Checklist (do the day before)

- [ ] Accounts + keys: Google AI Studio, Groq, Pexels, Pixabay, Cloudflare (Workers AI), Hugging Face, Vercel, GitHub
- [ ] Install: Python 3.11, Node 20, FFmpeg (with libass), Git, optionally Ollama + a small model
- [ ] Download 8–10 royalty-free music tracks + fonts (Poppins, Inter, Noto Devanagari, Noto Gujarati)
- [ ] Create an account on Qoneqt, browse the Global Feed, note video length/format norms, caption style, popular communities → tune `community_profiles.yaml`
- [ ] Test that the venue Wi-Fi isn't needed for essentials: keep Ollama model + Piper voice downloaded as offline fallbacks; carry mobile hotspot
- [ ] Pre-render 3 backup videos of different topics
- [ ] Charge laptop, bring charger/extension, headphones

---

## 14. README.md Must Contain

1. One-line pitch + GIF/screenshot
2. Live demo URL + demo video link + Qoneqt published video link
3. Problem → solution (Qoneqt Global Feed at scale)
4. Architecture diagram + 12 stages table
5. Features (quality gate, fallbacks, batch, trends, export pack)
6. Tech stack (all free, ₹0/video)
7. Quick start (local), env vars table, `docker compose up`
8. Sample outputs (links to `samples/`)
9. Limitations & roadmap (direct Qoneqt API publishing, A/B hook testing, analytics feedback loop, personalization per community, GPU video models)
10. Team + license + AI-disclosure

---

## 15. Demo Script (3 min) → `docs/DEMO_SCRIPT.md`

- **0:00–0:20** Problem: creators can't make quality video at scale; Qoneqt feed needs fresh content.
- **0:20–0:50** Pick a live trend → choose community → Generate. Show pipeline timeline running.
- **0:50–1:40** Walk through script (hook), scenes, quality gate catching & fixing a weak hook (show the before/after score), fallback badge.
- **1:40–2:15** Final video plays in phone frame; QA report all green; export pack.
- **2:15–2:40** Batch mode: 5 videos queued.
- **2:40–3:00** Show video **live on Qoneqt Global Feed**; cost ₹0; roadmap; thank you.

### Judge Q&A prep
- *"What if an API fails?"* → fallback chains, show health page.
- *"How does it scale?"* → stateless stages, queue abstraction, swap SQLite→Postgres, workers horizontally.
- *"How do you ensure quality/safety?"* → critic gate, fact-grounding, safety filter, QA checks.
- *"Why not AI video models?"* → GPU cost/latency/reliability; our approach renders in ~60–120s on free CPU; pluggable provider exists.
- *"What's novel?"* → community-aware + self-critiquing + QA'd + batch + trend loop.

---

## 16. `AGENTS.md` (put in repo root for Antigravity)

```
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

## 17. Antigravity Build Prompts (paste one at a time, in order)

**Phase 1** — "Read QONEQTFORGE_MASTER_SPEC.md. Create the full repo structure from §4 with empty-but-valid files, `.env.example`, `requirements.txt`, `Makefile`, `AGENTS.md`, `.gitignore`. Initialize git. Don't write logic yet."

**Phase 2** — "Implement `schemas.py`, `config.py`, `utils/json_repair.py`, `providers/llm_*`, `llm_router.py` with fallback and tests with mocked failures."

**Phase 3** — "Implement stages s01–s05 and prompts per §6. Add `scripts/generate_sample.py` that runs ingest→critic and prints JSON. Show a real run."

**Phase 4** — "Implement image providers + router, `tts_edge.py`, `asr_whisper.py`, stages s06–s09."

**Phase 5** — "Implement `video/*` and `s10_compose.py`, `s11_qa.py`, `s12_export.py` per §8–9. Produce a real 30s MP4 and verify with ffprobe."

**Phase 6** — "Implement orchestrator, worker, SQLite models, SSE, API per §10, rate limiting. Add tests."

**Phase 7** — "Build the Next.js frontend per §11, consuming the API and SSE. Make it polished, responsive, dark theme."

**Phase 8** — "Create Dockerfile for HF Spaces (port 7860, ffmpeg installed, non-root), `docker-compose.yml`, GitHub Actions CI, Vercel config. Provide deploy steps."

**Phase 9** — "Write README per §14, docs/ARCHITECTURE.md with a diagram, DEMO_SCRIPT.md, PPT_OUTLINE.md. Generate 3 sample videos into `samples/`."

**Phase 10** — "Hardening pass: error states in UI, empty states, timeouts, cleanup job, health page, accessibility, lint, tests green."

---

## 18. Deployment Steps (short)

**Backend → Hugging Face Space (Docker)**: create Space (SDK: Docker) → push `backend/` as repo root with Dockerfile listening on `7860` → add secrets (GEMINI_API_KEY, GROQ_API_KEY, PEXELS_API_KEY, CF keys) → note: free CPU is slow; use `faster-whisper tiny`, cap duration to 45s on public demo, keep `MAX_CONCURRENT_JOBS=1–2`.
**Frontend → Vercel**: import repo, root `frontend/`, set `NEXT_PUBLIC_API_URL` to the Space URL (`https://<user>-<space>.hf.space`), enable CORS on backend for the Vercel domain.
**Backup**: Cloudflare Tunnel from your laptop to the local backend if the Space is slow during judging.

---

## 19. Round 2 PPT Outline (shortlist stage) → `docs/PPT_OUTLINE.md`

1. Title + team
2. Problem (feed needs quality video at scale)
3. Solution: QoneqtForge in one line + screenshot mock
4. Architecture (12 stages)
5. AI engine: LLM agents + critic loop + multimodal visuals
6. Reliability: fallbacks, QA checks, ₹0 cost
7. Qoneqt-fit: community profiles, CTA, export pack, feed format
8. Scale: batch + trends + queue
9. Implementation plan for 8 hours (timeline §12)
10. Impact + roadmap + team strengths

---

## 20. Definition of Done

- [ ] `make dev` runs backend + frontend locally
- [ ] Topic → final 1080×1920 MP4 in ≤ 3 min on CPU, with captions, voice, music
- [ ] Critic gate visibly improves a draft
- [ ] Provider fallback proven (kill a key → still works)
- [ ] Batch of 5 works
- [ ] Public live URL works for a stranger
- [ ] README, demo video, samples ready; repo public
- [ ] **One video published on Qoneqt Global Feed** (link saved in README)
- [ ] Tests + CI green

---

## 21. Common Failure Points & Fixes

| Problem | Fix |
|---|---|
| Pollinations slow/blocked | retry with new seed → Cloudflare → Pexels |
| LLM returns bad JSON | repair → re-ask → next provider |
| FFmpeg subtitles font missing | pass `fontsdir`, bundle fonts, verify libass |
| Hindi/Gujarati text boxes (tofu) | use Noto Sans Devanagari / Gujarati fonts in ASS |
| HF Space render too slow | lower fps to 24, `-preset veryfast`, shorter durations, pre-render samples |
| Audio/captions drift | derive scene timing from actual audio durations |
| Venue Wi-Fi dies | hotspot + Ollama/Piper offline fallback + pre-rendered videos |
| Memory limit on free host | process scenes sequentially, delete intermediates, `-threads 2` |

---

**Final reminder to Antigravity:** quality > quantity of features. Every stage must really work, be demonstrable, and be explainable. Ship early, polish after.
