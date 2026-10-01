# Round 2 PPT Outline

## QoneqtForge — AI-Powered Content Pipeline for Qoneqt

### Slide 1: Title
- **QoneqtForge**: AI-Powered Content Pipeline for Qoneqt Global Feed
- Team name, hackathon name, date

### Slide 2: The Problem
- Qoneqt's Global Feed needs fresh, quality video content at scale
- Manual content creation: hours per video, inconsistent quality
- Creators can't keep up with feed demand
- Key stat: Quality short-form video takes 2-4 hours manually

### Slide 3: Our Solution
- QoneqtForge: Topic/Trend → Publish-ready vertical video in < 2 minutes
- One-line: "An AI pipeline that turns ideas into Qoneqt-ready videos — automatically, reliably, at scale, for ₹0"
- Screenshot/mockup of the app

### Slide 4: Architecture Overview
- 12-stage pipeline diagram
- Multi-agent system: researcher, writer, critic, composer
- Each stage: idempotent, logged, timed, resumable

### Slide 5: AI Engine
- LLM Agents: Research → Script → Scenes → Critic (quality gate)
- Self-critiquing loop: auto-revises weak hooks/scripts (show before/after score)
- Fact-grounded: only uses researched facts (no hallucination)
- Community-aware: adapts tone, CTA, hashtags per Qoneqt community

### Slide 6: Reliability & Cost
- Triple fallback chains: Gemini → Groq → Ollama (LLM), Pollinations → CF → Pexels (images)
- Automated QA: resolution, loudness, duration, caption coverage checks
- Total cost per video: **₹0** (100% free-tier stack)
- Never fails on stage — always produces output

### Slide 7: Qoneqt Fit
- Community profiles (tech, startup, fitness, etc.) → tailored content
- CTA drives Qoneqt engagement (comments, community joins, shares)
- Export Pack: MP4 + caption + hashtags ready to publish in 30 seconds
- Vertical 9:16 format, feed-optimized captions, hook-first storytelling

### Slide 8: Scale & Batch
- Batch mode: 1 trend list → 5 videos in queue
- Trend ingestion: auto-discover topics from HN/Reddit/Google Trends
- Background worker with progress tracking
- Repeatable: same quality every time

### Slide 9: Implementation Plan (8 Hours)
- Hour 0-1.5: Backend + LLM pipeline
- Hour 1.5-3: Media generation + first video
- Hour 3-4: API + orchestration
- Hour 4-5.5: Frontend UI
- Hour 5.5-6.5: Deploy + generate real videos
- Hour 6.5-8: Demo prep + polish

### Slide 10: Impact & Roadmap
- **Now**: Topic → video in < 2 min, ₹0, batch mode
- **Next**: Direct Qoneqt API publishing, A/B hook testing, analytics feedback loop
- **Future**: Personalization per community, GPU video models, multi-language expansion
- Team strengths + thank you
