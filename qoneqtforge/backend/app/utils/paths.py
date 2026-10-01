"""Path management utilities for job artifacts."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.config import settings


def get_job_dir(job_id: str) -> Path:
    """Get or create the directory for a specific job."""
    job_dir = settings.jobs_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def get_stage_output_path(job_id: str, stage_name: str, filename: str) -> Path:
    """Get the path for a stage output file."""
    job_dir = get_job_dir(job_id)
    return job_dir / f"{stage_name}_{filename}"


def get_scene_image_path(job_id: str, scene_idx: int) -> Path:
    """Get the path for a scene image."""
    return get_stage_output_path(job_id, "visuals", f"scene_{scene_idx}.png")


def get_scene_audio_path(job_id: str, scene_idx: int) -> Path:
    """Get the path for a scene audio file."""
    return get_stage_output_path(job_id, "voice", f"scene_{scene_idx}.mp3")


def get_scene_timings_path(job_id: str, scene_idx: int) -> Path:
    """Get the path for scene timing data."""
    return get_stage_output_path(job_id, "voice", f"scene_{scene_idx}_timings.json")


def get_captions_path(job_id: str) -> Path:
    """Get the path for the ASS captions file."""
    return get_stage_output_path(job_id, "captions", "captions.ass")


def get_music_path(job_id: str) -> Path:
    """Get the path for the processed music track."""
    return get_stage_output_path(job_id, "music", "music_ducked.mp3")


def get_final_video_path(job_id: str) -> Path:
    """Get the path for the final composed video."""
    return get_stage_output_path(job_id, "compose", "final.mp4")


def get_thumbnail_path(job_id: str) -> Path:
    """Get the path for the video thumbnail."""
    return get_stage_output_path(job_id, "export", "thumbnail.jpg")


def get_export_dir(job_id: str) -> Path:
    """Get the export directory for a job."""
    export_dir = get_job_dir(job_id) / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def cleanup_job(job_id: str) -> None:
    """Remove all artifacts for a job."""
    job_dir = settings.jobs_dir / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
