"""Async job worker — processes pipeline jobs from a queue."""

from __future__ import annotations

import asyncio
import logging

from app.config import settings
from app.core.orchestrator import run_pipeline
from app.schemas import BriefSpec

logger = logging.getLogger(__name__)

# Global job queue
_job_queue: asyncio.Queue | None = None
_workers: list[asyncio.Task] = []


def get_queue() -> asyncio.Queue:
    """Get or create the global job queue."""
    global _job_queue
    if _job_queue is None:
        _job_queue = asyncio.Queue(maxsize=100)
    return _job_queue


async def submit_job(job_id: str, brief: BriefSpec) -> None:
    """Submit a job to the processing queue."""
    queue = get_queue()
    await queue.put((job_id, brief))
    logger.info("Job %s queued (queue size: %d)", job_id, queue.qsize())


async def _worker(worker_id: int) -> None:
    """Background worker that processes jobs from the queue."""
    queue = get_queue()
    logger.info("Worker %d started", worker_id)

    while True:
        try:
            job_id, brief = await queue.get()
            logger.info("Worker %d processing job %s", worker_id, job_id)

            try:
                await run_pipeline(job_id, brief)
                logger.info("Worker %d completed job %s", worker_id, job_id)
            except Exception as e:
                logger.error("Worker %d job %s failed: %s", worker_id, job_id, e)
            finally:
                queue.task_done()

        except asyncio.CancelledError:
            logger.info("Worker %d shutting down", worker_id)
            break
        except Exception as e:
            logger.error("Worker %d unexpected error: %s", worker_id, e)
            await asyncio.sleep(1)


async def start_workers(count: int | None = None) -> None:
    """Start background workers."""
    global _workers
    if count is None:
        count = settings.max_concurrent_jobs

    for i in range(count):
        task = asyncio.create_task(_worker(i))
        _workers.append(task)

    logger.info("Started %d pipeline workers", count)


async def stop_workers() -> None:
    """Stop all workers gracefully."""
    for task in _workers:
        task.cancel()
    if _workers:
        await asyncio.gather(*_workers, return_exceptions=True)
    _workers.clear()
    logger.info("All workers stopped")


def get_active_job_count() -> int:
    """Get the number of jobs currently being processed or queued."""
    queue = get_queue()
    return queue.qsize() + sum(1 for t in _workers if not t.done())
