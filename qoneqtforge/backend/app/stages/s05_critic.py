"""Stage 5: Critic / Quality Gate — LLM-powered script review with auto-revision loop."""

from __future__ import annotations

import json
import logging

from app.providers import llm_router
from app.schemas import BriefSpec, CriticReport, ResearchResult, ScenePlan, Script
from app.utils.paths import get_job_dir

logger = logging.getLogger(__name__)

CRITIC_SYSTEM_PROMPT = """You are a strict viral-content editor reviewing a short-form video script.
Score each dimension 1-10: hook, clarity, factuality, pacing, safety, community_fit.
Calculate overall as weighted mean (hook 30%, clarity 20%, factuality 20%, pacing 10%, safety 10%, community_fit 10%).
pass_ = overall >= 7.5 AND safety >= 8 AND factuality >= 8.
Be strict but fair. List specific, actionable issues."""


async def run(
    job_id: str,
    brief: BriefSpec,
    script: Script,
    scene_plan: ScenePlan,
    research: ResearchResult,
) -> CriticReport:
    """Run the quality gate critic on the script and scene plan.

    This is the self-critiquing loop — if the script doesn't pass,
    it will be sent back for revision (handled by the orchestrator).
    """
    logger.info("[%s] Stage 5: Critic — evaluating script quality", job_id)

    # Format inputs for the critic
    facts_text = "\n".join(f"- {fact}" for fact in research.facts)
    script_text = json.dumps(script.model_dump(), indent=2)
    scenes_text = json.dumps(scene_plan.model_dump(), indent=2)

    prompt = f"""Review this short-form video script and scene plan.

SCRIPT:
{script_text}

SCENE PLAN:
{scenes_text}

ORIGINAL FACTS:
{facts_text}

COMMUNITY: {brief.community}
TONE: {brief.tone}
LANGUAGE: {brief.language}

Score 1-10 on: hook, clarity, factuality, pacing, safety, community_fit.
Calculate weighted overall (hook 30%, clarity 20%, factuality 20%, pacing 10%, safety 10%, community_fit 10%).
Set pass_ = overall >= 7.5 AND safety >= 8 AND factuality >= 8.

Return JSON with: scores (dict), overall (float), issues (list), must_fix (list), pass_ (bool)."""

    result = await llm_router.complete_json(
        prompt=prompt,
        schema=CriticReport,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        temperature=0.3,  # Low temperature for consistent evaluation
    )

    # Verify the overall score calculation
    weights = {
        "hook": 0.3,
        "clarity": 0.2,
        "factuality": 0.2,
        "pacing": 0.1,
        "safety": 0.1,
        "community_fit": 0.1,
    }
    calculated_overall = sum(
        result.scores.get(dim, 5) * weight for dim, weight in weights.items()
    )
    result.overall = round(calculated_overall, 1)

    # Enforce pass criteria
    result.pass_ = (
        result.overall >= 7.5
        and result.scores.get("safety", 0) >= 8
        and result.scores.get("factuality", 0) >= 8
    )

    # Save critic report
    job_dir = get_job_dir(job_id)
    critic_path = job_dir / "critic_report.json"
    with open(critic_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    status = "✓ PASSED" if result.pass_ else "✗ FAILED"
    logger.info(
        "[%s] %s Critic — overall=%.1f, scores=%s (provider: %s)",
        job_id,
        status,
        result.overall,
        result.scores,
        llm_router.get_last_provider(),
    )

    if not result.pass_ and result.must_fix:
        logger.info("[%s] Must fix: %s", job_id, result.must_fix)

    return result
