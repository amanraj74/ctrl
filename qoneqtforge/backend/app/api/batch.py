"""Batch API — create multiple jobs at once."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.core.worker import submit_job
from app.db import get_session
from app.models import Job
from app.schemas import BatchCreateRequest, BriefSpec

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/batch", tags=["batch"])


@router.post("")
async def create_batch(request: BatchCreateRequest):
    """Create multiple video generation jobs from a list of topics."""
    job_ids = []

    for topic in request.topics:
        brief = BriefSpec(
            topic=topic,
            community=request.community,
            tone=request.tone,
            language=request.language,
            duration_sec=request.duration_sec,
        )

        with get_session() as session:
            job = Job(
                brief_spec_json=brief.model_dump_json(),
                status="queued",
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            job_id = job.id

        await submit_job(job_id, brief)
        job_ids.append(job_id)

    logger.info("Batch created: %d jobs", len(job_ids))
    return {"job_ids": job_ids, "count": len(job_ids)}
