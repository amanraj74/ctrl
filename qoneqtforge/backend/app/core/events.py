"""SSE (Server-Sent Events) pub/sub system for real-time job updates."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Per-job event queues for SSE subscribers
_subscribers: dict[str, list[asyncio.Queue]] = {}


def subscribe(job_id: str) -> asyncio.Queue:
    """Subscribe to events for a specific job."""
    queue: asyncio.Queue = asyncio.Queue()
    if job_id not in _subscribers:
        _subscribers[job_id] = []
    _subscribers[job_id].append(queue)
    logger.debug("SSE subscriber added for job %s (total: %d)", job_id, len(_subscribers[job_id]))
    return queue


def unsubscribe(job_id: str, queue: asyncio.Queue) -> None:
    """Unsubscribe from job events."""
    if job_id in _subscribers:
        try:
            _subscribers[job_id].remove(queue)
        except ValueError:
            pass
        if not _subscribers[job_id]:
            del _subscribers[job_id]


def emit(job_id: str, event_type: str, data: Any = None) -> None:
    """Emit an event to all subscribers of a job."""
    if job_id not in _subscribers:
        return

    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for queue in _subscribers[job_id]:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("SSE queue full for job %s, dropping event", job_id)


def emit_stage_start(job_id: str, stage_name: str) -> None:
    """Emit a stage start event."""
    emit(job_id, "stage_start", {"stage": stage_name})


def emit_stage_complete(job_id: str, stage_name: str, duration_ms: float, details: Any = None) -> None:
    """Emit a stage completion event."""
    emit(job_id, "stage_complete", {
        "stage": stage_name,
        "duration_ms": round(duration_ms, 1),
        "details": details,
    })


def emit_stage_failed(job_id: str, stage_name: str, error: str) -> None:
    """Emit a stage failure event."""
    emit(job_id, "stage_failed", {"stage": stage_name, "error": error})


def emit_log(job_id: str, stage_name: str, level: str, message: str) -> None:
    """Emit a log event."""
    emit(job_id, "log", {"stage": stage_name, "level": level, "message": message})


def emit_job_complete(job_id: str, video_url: str | None = None) -> None:
    """Emit a job completion event."""
    emit(job_id, "job_complete", {"video_url": video_url})


def emit_job_failed(job_id: str, error: str) -> None:
    """Emit a job failure event."""
    emit(job_id, "job_failed", {"error": error})


async def event_generator(job_id: str):
    """Async generator yielding SSE events for a job.

    Used by the SSE endpoint to stream events to the frontend.
    """
    queue = subscribe(job_id)
    try:
        while True:
            event = await queue.get()
            yield {
                "event": event["type"],
                "data": json.dumps(event),
            }
            # Stop on terminal events
            if event["type"] in ("job_complete", "job_failed"):
                break
    finally:
        unsubscribe(job_id, queue)
