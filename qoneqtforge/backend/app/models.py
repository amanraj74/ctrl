"""Database models for jobs, stages, assets, and logs."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(SQLModel, table=True):
    """A video generation job."""

    __tablename__ = "jobs"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    status: str = Field(default="queued")  # queued, processing, completed, failed
    brief_spec_json: str = Field(default="{}")  # JSON-serialized BriefSpec
    current_stage: str | None = None
    error: str | None = None
    video_path: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class StageRun(SQLModel, table=True):
    """A single pipeline stage execution record."""

    __tablename__ = "stage_runs"

    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    stage_name: str
    status: str = Field(default="pending")  # pending, running, completed, failed, skipped
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    output_json: str | None = None  # JSON-serialized stage output
    error: str | None = None


class Asset(SQLModel, table=True):
    """An artifact produced by a pipeline stage."""

    __tablename__ = "assets"

    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    stage_name: str
    asset_type: str  # image, audio, video, subtitle, json, text
    file_path: str
    metadata_json: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class LogLine(SQLModel, table=True):
    """A log entry from a pipeline stage."""

    __tablename__ = "log_lines"

    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    stage_name: str
    level: str = "info"  # debug, info, warn, error
    message: str
    timestamp: datetime = Field(default_factory=utcnow)
