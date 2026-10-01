"""Jobs API — create, get, stream events, regenerate scenes."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.core.events import event_generator
from app.core.worker import submit_job
from app.db import get_session
from app.models import Job, StageRun
from app.schemas import BriefSpec, JobCreateRequest, JobResponse, JobStatus, StageInfo, StageStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=dict)
async def create_job(request: JobCreateRequest):
    """Create a new video generation job."""
    brief = request.brief

    # Create job in DB
    with get_session() as session:
        job = Job(
            brief_spec_json=brief.model_dump_json(),
            status="queued",
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    logger.info("Job created: %s — topic='%s'", job_id, brief.topic[:60])

    # Submit to worker queue
    await submit_job(job_id, brief)

    return {"id": job_id, "status": "queued"}


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get job details including stage status and timing."""
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get stage runs
        stages = session.query(StageRun).filter(StageRun.job_id == job_id).all()

        brief = BriefSpec.model_validate_json(job.brief_spec_json)

        stage_infos = [
            StageInfo(
                name=s.stage_name,
                status=StageStatus(s.status),
                started_at=s.started_at,
                completed_at=s.completed_at,
                duration_ms=s.duration_ms,
                error=s.error,
            )
            for s in stages
        ]

        # Determine video URL
        video_url = None
        if job.video_path and Path(job.video_path).exists():
            video_url = f"/api/jobs/{job_id}/video"

        return JobResponse(
            id=job.id,
            status=JobStatus(job.status),
            brief=brief,
            stages=stage_infos,
            current_stage=job.current_stage,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error=job.error,
            video_url=video_url,
        )


@router.get("/{job_id}/events")
async def stream_events(job_id: str):
    """SSE endpoint — stream real-time pipeline events for a job."""
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    return EventSourceResponse(event_generator(job_id))


@router.get("/{job_id}/video")
async def get_video(job_id: str):
    """Serve the generated video file."""
    from fastapi.responses import FileResponse

    with get_session() as session:
        job = session.get(Job, job_id)
        if not job or not job.video_path:
            raise HTTPException(status_code=404, detail="Video not found")

    if not Path(job.video_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        job.video_path,
        media_type="video/mp4",
        filename=f"qoneqtforge_{job_id[:8]}.mp4",
    )
