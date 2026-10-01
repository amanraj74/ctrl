"""Stage 2: Research — Gather grounded facts about the topic using LLM."""

from __future__ import annotations

import json
import logging

from app.providers import llm_router
from app.schemas import BriefSpec, ResearchResult
from app.utils.paths import get_job_dir

logger = logging.getLogger(__name__)

RESEARCH_SYSTEM_PROMPT = """You are a research assistant. Given a TOPIC, produce 5-8 factual bullet points.
Each fact must be specific, verifiable, and interesting.
Include numbers, dates, or names where possible.
Do NOT make up statistics. If unsure, say "reportedly" or "approximately".
Return a JSON object with:
- "facts": array of 5-8 fact strings
- "sources": array of source strings (can be empty)"""


async def run(job_id: str, brief: BriefSpec) -> ResearchResult:
    """Research the topic and extract grounded facts.

    These facts become the ONLY source of truth for the script stage,
    preventing LLM hallucination.
    """
    logger.info("[%s] Stage 2: Research — topic=%s", job_id, brief.topic[:60])

    prompt = f"Research this topic thoroughly and provide 5-8 specific, factual bullet points:\n\nTOPIC: {brief.topic}"

    result = await llm_router.complete_json(
        prompt=prompt,
        schema=ResearchResult,
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        temperature=0.5,  # Lower temperature for factual accuracy
    )

    # Save research output
    job_dir = get_job_dir(job_id)
    research_path = job_dir / "research.json"
    with open(research_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(
        "[%s] ✓ Research complete — %d facts gathered (provider: %s)",
        job_id,
        len(result.facts),
        llm_router.get_last_provider(),
    )
    return result
