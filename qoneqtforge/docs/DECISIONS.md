# Design Decisions

This document records every non-obvious design choice made during development.

## Architecture

### Image + Ken Burns vs AI Video Models
**Decision**: Use AI-generated images with Ken Burns motion effects instead of AI video generation models.
**Rationale**: AI video models (Wan, LTX, etc.) require GPU resources which are not available on free-tier hosting. Our approach renders professional-looking videos in ~60-120 seconds on free CPU, producing results visually comparable to top short-form feed content.

### SQLite vs PostgreSQL
**Decision**: Use SQLite via SQLModel.
**Rationale**: Zero setup, single file database, perfect for hackathon and free-tier deployment. Can be swapped to PostgreSQL later via SQLModel's abstraction.

### asyncio Worker vs Celery/Redis
**Decision**: In-process asyncio queue worker.
**Rationale**: No extra services needed, simpler deployment, sufficient throughput for demo (2 concurrent jobs). The abstraction allows swapping to Celery if scaling is needed.

### SSE vs WebSocket
**Decision**: Server-Sent Events for real-time updates.
**Rationale**: Simpler implementation, one-directional (server→client) which is all we need for progress updates, better browser support, automatic reconnection.

### edge-tts vs Paid TTS
**Decision**: Microsoft edge-tts library.
**Rationale**: Free neural voices in multiple languages (English, Hindi, Gujarati), provides word-level timing data for caption sync, no API key needed.

## Content Strategy

### Hook-First Storytelling
**Decision**: Every script must start with a hook ≤ 12 words.
**Rationale**: Vertical feed viewers decide in 2 seconds. Hook-first approach is proven to increase retention.

### Community Profiles
**Decision**: Pre-defined community profiles (tech, startup, fitness, etc.) that adapt tone, CTA, and hashtags.
**Rationale**: Qoneqt is community-first; showing we understand this differentiation impresses judges.

---
*Updated as decisions are made during development.*
