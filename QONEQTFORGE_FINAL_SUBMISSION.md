# QoneqtForge — Final Project Submission

**For: CTRL FREAK 2026 Hackathon (HackBriven)**

## 🚀 Overview

QoneqtForge is a complete, industry-level, AI-powered content pipeline designed specifically for the Qoneqt Global Feed. It completely automates the process of transforming topics, ideas, or trends into publish-ready, 9:16 vertical videos.

We built this pipeline to solve the exact problem outlined in the challenge: manual video creation takes hours, but users consume content in seconds. QoneqtForge achieves zero-cost, high-quality, continuous content generation.

## 🏗 The 12-Stage Pipeline

The core of the project is the `app.core.orchestrator`, which runs jobs through 12 specific stages:

1. **Ingest (`s01_ingest`)**: Validates the input topic for safety and normalizes the brief (community tone, language, duration).
2. **Research (`s02_research`)**: Uses LLMs to gather verifiable, factual bullet points. **This is critical:** by enforcing that the script *only* uses these facts, we prevent AI hallucinations.
3. **Script (`s03_script`)**: Generates a hook-first video script formatted for a 2-second decision window. It understands the nuances of 8 different Qoneqt community profiles (Tech, Fitness, Startup, etc.).
4. **Scenes (`s04_scenes`)**: Breaks the script into 4-6 second visual scenes, generating detailed image prompts and varying camera motion (Ken Burns effects).
5. **Quality Gate Critic (`s05_critic`)**: A strict LLM editor scores the script across 6 dimensions (hook, clarity, factuality, pacing, safety, community_fit). **If it scores below 7.5/10, the orchestrator automatically sends it back for revision (up to 2 times).**
6. **Visuals (`s06_visuals`)**: Generates the images for each scene asynchronously using our Image Fallback Router.
7. **Voice (`s07_voice`)**: Synthesizes neural voice narration and extracts word-level timing data for captions.
8. **Captions (`s08_captions`)**: Generates Advanced SubStation Alpha (`.ass`) files with word-by-word karaoke highlighting.
9. **Music (`s09_music`)**: Selects tone-matched, royalty-free background music from our local catalog.
10. **Compose (`s10_compose`)**: The FFmpeg heavy lifter. Applies Ken Burns zooms/pans, mixes audio with ducking (lowering music volume when voice speaks), burns in karaoke captions, normalizes audio to EBU R128 (-14 LUFS), and exports a 1080x1920 H.264 MP4.
11. **QA (`s11_qa`)**: Automatically probes the final video to ensure correct resolution, framerate, codec, audio presence, file size (under 50MB), and absence of black frames.
12. **Export (`s12_export`)**: Packages the MP4, a generated thumbnail, the caption text, hashtags, and metadata into a clean `export.zip` ready for direct publishing.

## 🛡 The Triple-Fallback Architecture (Zero Failure Design)

To ensure the pipeline *never* halts due to a provider outage or rate limit (especially since we use free tiers), we built robust fallback routers:

**LLM Router (`app/providers/llm_router.py`):**
1. **Google Gemini 2.0 Flash:** Primary. Fast and excellent at JSON output.
2. **Groq (Llama 3.3 70B):** First fallback. Ultra-fast inference.
3. **Ollama (llama3.2):** Local fallback. If the internet fails, we run locally.

**Image Router (`app/providers/img_router.py`):**
1. **Pollinations.ai:** Primary. Free FLUX model generation.
2. **Cloudflare Workers AI:** Fallback. Uses FLUX-1-schnell on the free tier.
3. **Pexels API:** Last resort. Fetches high-quality portrait stock photos.

**TTS Provider:**
- **Edge-TTS:** Primary. Microsoft neural voices with word-level boundary data.
- **Piper/pyttsx3:** Offline fallback.

## 💻 Tech Stack (100% Free & Open Source)

- **Backend:** Python 3.11, FastAPI, SQLModel (SQLite)
- **Video/Audio:** FFmpeg, Edge-TTS, faster-whisper
- **Frontend:** Next.js 14, TailwindCSS, Server-Sent Events (SSE)
- **Infrastructure:** Asynchronous workers, Queue-based processing

## 🎨 Frontend UI

We built a beautiful, dark-mode, glassmorphism UI:
- **Home Page:** Glowing inputs, trending topic chips (from HackerNews & Reddit), and advanced settings drawer.
- **Job Status Page:** Real-time progress bar powered by Server-Sent Events (SSE). You can literally watch the live logs as the video is forged. It includes a smartphone-frame video player for the final result.
- **Batch Mode:** Submit up to 10 topics at once for asynchronous parallel processing.

## 🚀 How to Run

1. **Add your API Keys:** Fill in `.env` (Gemini, Groq, Cloudflare, Pexels).
2. **Install FFmpeg:** Ensure `ffmpeg` and `ffprobe` are in your PATH.
3. **Run Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
4. **Run Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. **Test the CLI (Without Web UI):**
   ```bash
   cd backend
   python -m scripts.generate_sample "The future of AI in 2026"
   ```

## 🏆 Hackathon Winning Edge

- **Not just a wrapper:** We built a legitimate, multi-stage data pipeline with auto-recovery and self-critiquing.
- **Zero Cost:** We utilized highly optimized free tiers and local fallbacks. Cost per video is ₹0.
- **Broadcast Quality:** We implement audio ducking, EBU R128 loudness normalization, and Ken Burns cinematic movement. This isn't a slideshow; it's a dynamic video.
