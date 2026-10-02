"""Core data contracts for the QoneqtForge pipeline.

These Pydantic v2 models define the exact shape of data flowing
between pipeline stages. All LLM outputs are validated against these schemas.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# ─── Enums ───────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


STAGE_NAMES: list[str] = [
    "ingest",
    "research",
    "script",
    "scenes",
    "critic",
    "visuals",
    "voice",
    "captions",
    "music",
    "compose",
    "qa",
    "export",
]


# ─── Pipeline Input ──────────────────────────────────────────────────

class BriefSpec(BaseModel):
    """Input specification for a video generation job."""

    topic: str = Field(..., min_length=3, max_length=500, description="The topic, prompt, idea, or trend")
    source_type: Literal["topic", "prompt", "idea", "trend"] = "topic"
    community: str = Field(default="general", description="Community profile key from community_profiles.yaml")
    tone: Literal["energetic", "calm", "funny", "inspiring", "explainer"] = "energetic"
    language: Literal["en", "hi", "gu"] = "en"
    duration_sec: Literal[20, 30, 45, 60] = 30
    voice: str | None = Field(default=None, description="TTS voice name, e.g. en-IN-NeerjaNeural")
    visual_style: str = Field(
        default="cinematic",
        description="Visual style: cinematic, illustration, flat-vector, photoreal",
    )


# ─── Research Output ─────────────────────────────────────────────────

class ResearchResult(BaseModel):
    """Output from the research stage."""

    facts: list[str] = Field(..., min_length=3, max_length=10, description="5-8 factual bullet points")
    sources: list[str] = Field(default_factory=list, description="Source URLs or references")


# ─── Script ──────────────────────────────────────────────────────────

class Beat(BaseModel):
    """A story beat in the script."""

    role: Literal["hook", "context", "insight", "proof", "cta"]
    text: str = Field(..., min_length=1)


class Script(BaseModel):
    """Complete script for a short-form video."""

    title: str = Field(..., min_length=3, max_length=100)
    hook: str = Field(..., max_length=100, description="Hook line, <= 12 words")
    beats: list[Beat] = Field(..., min_length=3, description="Story beats: hook, context, insights, proof, CTA")
    cta: str = Field(..., description="Call-to-action for Qoneqt engagement")
    caption: str = Field(..., max_length=300, description="Qoneqt post caption")
    hashtags: list[str] = Field(..., min_length=3, max_length=10, description="5-8 hashtags")
    facts_used: list[str] = Field(default_factory=list, description="Facts referenced in the script")


# ─── Scene Plan ──────────────────────────────────────────────────────

class Scene(BaseModel):
    """A single visual scene in the video."""

    idx: int = Field(..., ge=0)
    narration: str = Field(..., min_length=1, description="Verbatim narration text for this scene")
    on_screen_text: str | None = Field(default=None, max_length=40, description="On-screen text, <= 6 words")
    visual_prompt: str = Field(..., description="Detailed image generation prompt")
    visual_source: Literal["ai_image", "stock"] = "ai_image"
    stock_query: str | None = Field(default=None, description="Search query for stock photos if visual_source=stock")
    motion: Literal["zoom_in", "zoom_out", "pan_left", "pan_right", "tilt_up"] = "zoom_in"
    duration_sec: float = Field(..., gt=0, le=30, description="Planned duration in seconds")


class ScenePlan(BaseModel):
    """Complete scene plan for the video."""

    style_prefix: str = Field(
        ...,
        description="Shared style prefix for all image prompts, e.g. 'cinematic, volumetric light, teal-orange grade'",
    )
    scenes: list[Scene] = Field(..., min_length=2, description="List of scenes covering the full script")


# ─── Critic / Quality Gate ───────────────────────────────────────────

class CriticReport(BaseModel):
    """Output from the critic/quality gate stage."""

    scores: dict[str, int] = Field(
        ...,
        description="Scores 1-10 for: hook, clarity, factuality, pacing, safety, community_fit",
    )
    overall: float = Field(..., ge=0, le=10, description="Weighted overall score")
    issues: list[str] = Field(default_factory=list, description="Issues found")
    must_fix: list[str] = Field(default_factory=list, description="Issues that must be fixed")
    pass_: bool = Field(..., description="Whether the script passes the quality gate")


# ─── QA Report ───────────────────────────────────────────────────────

class QACheck(BaseModel):
    """A single QA check result."""

    name: str
    passed: bool
    expected: str
    actual: str
    message: str = ""


class QAReport(BaseModel):
    """Output from the video QA stage."""

    checks: list[QACheck]
    all_passed: bool
    warnings: list[str] = Field(default_factory=list)


# ─── Export Pack ─────────────────────────────────────────────────────

class ExportPack(BaseModel):
    """Metadata for the export pack."""

    video_path: str
    thumbnail_path: str
    caption: str
    hashtags: list[str]
    metadata: dict
    script_md: str


# ─── API Request/Response ───────────────────────────────────────────

class JobCreateRequest(BaseModel):
    """Request to create a new video generation job."""

    brief: BriefSpec


class BatchCreateRequest(BaseModel):
    """Request to create multiple jobs from a list of topics."""

    topics: list[str] = Field(..., min_length=1, max_length=20)
    community: str = "general"
    tone: Literal["energetic", "calm", "funny", "inspiring", "explainer"] = "energetic"
    language: Literal["en", "hi", "gu"] = "en"
    duration_sec: Literal[20, 30, 45, 60] = 30


class StageInfo(BaseModel):
    """Information about a pipeline stage run."""

    name: str
    status: StageStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    error: str | None = None


class JobResponse(BaseModel):
    """Response containing full job details."""

    id: str
    status: JobStatus
    brief: BriefSpec
    stages: list[StageInfo] = Field(default_factory=list)
    current_stage: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    error: str | None = None
    video_url: str | None = None


class TrendItem(BaseModel):
    """A trending topic."""

    title: str
    source: str
    url: str | None = None
    score: int | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    providers: dict[str, bool] = Field(default_factory=dict)
    active_jobs: int = 0
    version: str = "1.0.0"
