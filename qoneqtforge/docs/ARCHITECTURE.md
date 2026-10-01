# QoneqtForge Architecture

## System Overview

QoneqtForge is a multi-stage AI pipeline that transforms topics into publish-ready vertical videos for the Qoneqt Global Feed.

## Architecture Diagram

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

## Pipeline Stages

| # | Stage | Input → Output | Notes |
|---|---|---|---|
| 1 | Ingest | topic/prompt/trend + options → BriefSpec | Options: community, tone, language, duration, voice |
| 2 | Research | BriefSpec → facts list | LLM + Wikipedia/RSS; prevents hallucination |
| 3 | Script | facts → Script (hook, beats, CTA) | Hook ≤ 12 words; community-aware CTA |
| 4 | Scene Plan | Script → ScenePlan (N scenes) | Strict JSON schema |
| 5 | Critic/Gate | Script+ScenePlan → score + fixes | Score < 7/10 → auto-revise (max 2 loops) |
| 6 | Visuals | scenes → images (AI + stock) | Parallel; fallback chain |
| 7 | Voice | narration → WAV + word timings | edge-tts |
| 8 | Captions | audio → word-level ASS subtitles | Karaoke highlight |
| 9 | Music | mood → track + ducked audio | FFmpeg sidechaincompress |
| 10 | Compose | everything → final.mp4 1080×1920 | Ken Burns, crossfades, overlays |
| 11 | QA | final.mp4 → checks | Resolution, duration, loudness, black frames |
| 12 | Export Pack | → MP4 + thumbnail + caption + hashtags | Ready to upload |

## Provider Fallback Strategy

Each provider layer has a fallback chain that ensures the pipeline never hard-fails:

- **LLM**: Gemini (primary) → Groq (fast fallback) → Ollama (offline)
- **Image**: Pollinations (no key) → Cloudflare Workers AI → Pexels stock
- **TTS**: edge-tts (primary) → Piper (offline) → pyttsx3 (last resort)

## Data Flow

1. User submits topic via Web UI or CLI
2. Backend creates a Job record in SQLite
3. Orchestrator runs 12 stages sequentially
4. Each stage writes artifacts to `data/jobs/<id>/`
5. SSE events stream progress to frontend in real-time
6. Final export pack is downloadable as ZIP
