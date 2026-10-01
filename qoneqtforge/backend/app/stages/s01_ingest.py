"""Stage 1: Ingest — Parse topic/prompt/idea/trend into a validated BriefSpec."""

from __future__ import annotations

import json
import logging

from app.schemas import BriefSpec
from app.utils.paths import get_job_dir
from app.utils.safety import is_content_safe

logger = logging.getLogger(__name__)


async def run(job_id: str, brief: BriefSpec) -> BriefSpec:
    """Ingest and validate the input brief.

    - Validates the topic for safety
    - Creates the job directory
    - Saves brief.json
    - Returns the validated BriefSpec
    """
    logger.info("[%s] Stage 1: Ingest — topic=%s", job_id, brief.topic[:60])

    # Safety check on topic
    is_safe, issues = is_content_safe(brief.topic)
    if not is_safe:
        logger.warning("[%s] Topic safety check failed: %s", job_id, issues)
        # Don't hard-fail, but log the warning. The critic gate will catch content issues later.

    # Create job directory
    job_dir = get_job_dir(job_id)
    logger.info("[%s] Job directory created: %s", job_id, job_dir)

    # Save brief spec
    brief_path = job_dir / "brief.json"
    with open(brief_path, "w", encoding="utf-8") as f:
        json.dump(brief.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info("[%s] ✓ Ingest complete — brief saved", job_id)
    return brief
