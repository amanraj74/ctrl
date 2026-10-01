"""Stage 3: Script — Generate a hook-first, community-aware script from facts."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from app.providers import llm_router
from app.schemas import BriefSpec, ResearchResult, Script
from app.utils.paths import get_job_dir
from app.utils.text import words_for_duration

logger = logging.getLogger(__name__)


def _load_community_profile(community: str) -> str:
    """Load community profile from YAML."""
    profiles_path = Path(__file__).parent.parent / "prompts" / "community_profiles.yaml"
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = yaml.safe_load(f)
        profile = profiles.get(community, profiles.get("general", {}))
        return yaml.dump(profile, default_flow_style=False)
    except Exception as e:
        logger.warning("Could not load community profile '%s': %s", community, e)
        return f"Community: {community} (general audience)"


SCRIPT_SYSTEM_PROMPT = """You are a senior short-form video writer for Qoneqt, a community-first social platform.
Write for a vertical feed where viewers decide in 2 seconds.
RULES:
- Hook <= 12 words, creates curiosity or a bold claim. No "Did you know".
- Structure: hook -> context -> 2 insights -> proof/example -> CTA.
- Spoken style, short sentences (<= 14 words), no jargon unless community requires.
- Use ONLY facts from FACTS. Never invent statistics.
- CTA invites interaction inside Qoneqt (comment, join the community, share).
OUTPUT: JSON matching the Script schema exactly. No markdown."""


async def run(
    job_id: str,
    brief: BriefSpec,
    research: ResearchResult,
    revision_feedback: str | None = None,
) -> Script:
    """Generate a script from researched facts.

    Args:
        job_id: Job identifier
        brief: The input brief specification
        research: Research results with grounded facts
        revision_feedback: Optional feedback from the critic gate for revision
    """
    logger.info("[%s] Stage 3: Script — community=%s, tone=%s", job_id, brief.community, brief.tone)

    # Calculate target word count
    target_words = words_for_duration(brief.duration_sec)

    # Load community profile
    community_profile = _load_community_profile(brief.community)

    # Build prompt
    facts_text = "\n".join(f"- {fact}" for fact in research.facts)

    prompt = f"""Write a short-form video script for the topic: "{brief.topic}"

Language: {brief.language}
Tone: {brief.tone}
Target duration: {brief.duration_sec} seconds (~{target_words} words)

COMMUNITY PROFILE:
{community_profile}

FACTS (use ONLY these):
{facts_text}
"""

    if revision_feedback:
        prompt += f"""
REVISION REQUIRED — fix these issues from the quality gate:
{revision_feedback}

Revise the script to address all must_fix issues while keeping the same facts and topic.
"""

    prompt += """
Return a JSON object with these exact fields:
- title: string (short catchy title)
- hook: string (12 words or fewer)
- beats: array of objects with "role" and "text" fields
  - roles must be: "hook", "context", "insight", "insight", "proof", "cta"
- cta: string (call-to-action for Qoneqt)
- caption: string (post caption, <= 300 chars)
- hashtags: array of 5-8 strings
- facts_used: array of facts referenced
"""

    result = await llm_router.complete_json(
        prompt=prompt,
        schema=Script,
        system_prompt=SCRIPT_SYSTEM_PROMPT,
        temperature=0.8,
    )

    # Save script
    job_dir = get_job_dir(job_id)
    script_path = job_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(
        "[%s] ✓ Script complete — hook='%s', %d beats (provider: %s)",
        job_id,
        result.hook[:50],
        len(result.beats),
        llm_router.get_last_provider(),
    )
    return result
