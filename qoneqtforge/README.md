# QoneqtForge 🎬

> **AI-Powered Content Pipeline for Qoneqt Global Feed** — Turn any topic into a publish-ready vertical video in under 2 minutes. Zero cost. Zero compromise.

[![CI](https://github.com/your-team/qoneqtforge/actions/workflows/ci.yml/badge.svg)](https://github.com/your-team/qoneqtforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 One-Line Pitch

**QoneqtForge** is a multi-agent AI pipeline that transforms topics, trends, and ideas into professional vertical videos for the Qoneqt Global Feed — with self-critiquing quality gates, triple-fallback providers, and batch production at ₹0/video.

## 🔗 Links

- **Live Demo**: [https://qoneqtforge.vercel.app](https://qoneqtforge.vercel.app)
- **API**: [https://your-space.hf.space](https://your-space.hf.space)
- **Demo Video**: [Watch (3 min)](https://link-to-demo-video)
- **Published on Qoneqt**: [View on Qoneqt Global Feed](https://link-to-qoneqt-post)

## 📋 Problem → Solution

### The Problem
Qoneqt's Global Feed needs fresh, engaging video content at scale. But creating quality short-form video takes 2-4 hours per video manually. Creators can't keep up with feed demand.

### The Solution
QoneqtForge automates the entire pipeline:

```
Topic/Trend → Research → Script → Scenes → Critic Gate → Visuals → Voice → Captions → Music → Video → QA → Export
```

**12 intelligent stages**, each with fallback chains, producing professional 1080×1920 videos optimized for the Qoneqt vertical feed.

## 🏗 Architecture

```
┌─────────────────┐   ┌──────────────────────────────────────────────────┐
│  Next.js Web UI │──▶│              FastAPI Backend                      │
│  (Vercel)       │◀──│  Pipeline Orchestrator (12 Stages)                │
└─────────────────┘   │  Provider Layer: LLM / Image / TTS (fallbacks)   │
                      │  SQLite DB · SSE Events · Job Queue              │
                      └──────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-Agent Pipeline** | 12 stages: research → script → visuals → video |
| 🔍 **Quality Gate** | LLM critic scores scripts on 6 dimensions, auto-revises weak content |
| 🔄 **Triple Fallbacks** | Gemini → Groq → Ollama (LLM), Pollinations → CF → Pexels (images) |
| 📊 **Batch Mode** | 1 trend list → 5 videos in queue, with progress tracking |
| 📡 **Trend Ingestion** | Auto-discover topics from HackerNews, Reddit |
| 🎙️ **Multi-Language** | English, Hindi, Gujarati — neural voice synthesis |
| 📱 **Feed-Optimized** | 1080×1920 9:16 vertical, karaoke captions, Ken Burns motion |
| 📦 **Export Pack** | MP4 + thumbnail + caption + hashtags in one ZIP |
| 💰 **₹0 Cost** | 100% free-tier stack — no credit card needed |
| 📈 **Observable** | Per-stage timing, logs, SSE live updates |

## 🛠 Tech Stack (All Free)

| Layer | Technology |
|---|---|
| **LLM** | Gemini 2.0 Flash → Groq (Llama 3.3 70B) → Ollama |
| **Images** | Pollinations.ai → Cloudflare Workers AI → Pexels |
| **Voice** | edge-tts (Microsoft neural voices) |
| **Captions** | faster-whisper + ASS karaoke subtitles |
| **Video** | FFmpeg + MoviePy (Ken Burns, crossfades, overlays) |
| **Backend** | FastAPI + SQLite + asyncio workers |
| **Frontend** | Next.js 14 + Tailwind + shadcn/ui + Framer Motion |
| **Deploy** | Hugging Face Spaces (backend) + Vercel (frontend) |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- FFmpeg (with libass support)

### Setup
```bash
git clone https://github.com/your-team/qoneqtforge.git
cd qoneqtforge

# Copy and fill environment variables
cp .env.example .env
# Edit .env with your API keys (all free tier)

# Install backend
cd backend && pip install -r requirements.txt

# Install frontend
cd ../frontend && npm install
```

### Run Locally
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Docker
```bash
docker compose up --build
```

### CLI Demo
```bash
cd backend
python -m scripts.generate_sample "AI is transforming education"
```

## 📁 Sample Outputs

See the [`samples/`](samples/) directory for pre-generated example videos with their export packs.

## 🚧 Limitations & Roadmap

**Current Limitations:**
- No direct Qoneqt API integration (manual upload via export pack)
- Free CPU rendering (~60-120s per video)
- Pollinations.ai rate limits may slow image generation

**Roadmap:**
- 🔜 Direct Qoneqt API publishing when available
- 🔜 A/B hook testing with engagement analytics
- 🔜 Analytics feedback loop (learn from published video performance)
- 🔜 Personalization per community member preferences
- 🔜 GPU video models (Wan, LTX) via pluggable provider
- 🔜 Multi-platform export (YouTube Shorts, Instagram Reels)

## 🏆 Built For

**CTRL FREAK 2026** · HackBriven · 8-hour offline hackathon · York·IE, Ahmedabad

## 📄 License

MIT — see [LICENSE](LICENSE)

## 🤖 AI Disclosure

This project uses AI for:
- Code generation (Antigravity)
- Content creation (LLM-generated scripts and visuals)
- Voice synthesis (edge-tts)

All generated video content includes "AI-generated" disclosure in metadata.

---

**Cost per video: ₹0 · Quality: Industry-grade · Built with ❤️ for Qoneqt**
