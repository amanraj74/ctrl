"""Stage 4: Scene Plan — Break script into visual scenes with motion and prompts."""

from __future__ import annotations

import json
import logging

from app.providers import llm_router
from app.schemas import BriefSpec, ScenePlan, Script
from app.utils.paths import get_job_dir

logger = logging.getLogger(__name__)

SCENES_SYSTEM_PROMPT = """You are a visual director for short-form vertical videos.
Convert scripts into detailed scene-by-scene plans for 9:16 vertical video.
Each scene needs a concrete image generation prompt — describe composition, lighting, camera angle.
NEVER include text in images. NEVER include real people or brand logos.
Vary the motion type between scenes — never repeat the same motion twice in a row.
Scene 1 must be the most visually striking (it's the hook that captures attention)."""


async def run(job_id: str, brief: BriefSpec, script: Script) -> ScenePlan:
    """Break the script into visual scenes with image generation prompts."""
    logger.info("[%s] Stage 4: Scenes — duration=%ds, style=%s", job_id, brief.duration_sec, brief.visual_style)

    # Calculate number of scenes (avg 4-6 sec per scene)
    n_scenes = max(3, brief.duration_sec // 5)

    # Build full narration text
    full_narration = " ".join(beat.text for beat in script.beats)

    prompt = f"""Convert this script into {n_scenes} scenes (average 4-6 seconds each).

SCRIPT TITLE: {script.title}
FULL NARRATION: {full_narration}

VISUAL STYLE: {brief.visual_style}

For each scene provide:
- idx: scene index (0-based)
- narration: verbatim slice of the script for this scene
- on_screen_text: <= 6 words overlay text (or null)
- visual_prompt: detailed image description (vertical 9:16, no text in image, no real people)
- visual_source: "ai_image" or "stock"
- stock_query: search term if stock (else null)
- motion: one of "zoom_in", "zoom_out", "pan_left", "pan_right", "tilt_up" (vary them!)
- duration_sec: estimated seconds

Return JSON with:
- style_prefix: shared visual style string for consistency
- scenes: array of scene objects

All narration text combined must cover the full script. No content should be missing."""

    result = await llm_router.complete_json(
        prompt=prompt,
        schema=ScenePlan,
        system_prompt=SCENES_SYSTEM_PROMPT,
        temperature=0.7,
    )

    # Validate: no consecutive duplicate motions
    for i in range(1, len(result.scenes)):
        if result.scenes[i].motion == result.scenes[i - 1].motion:
            # Rotate to next motion
            motions = ["zoom_in", "zoom_out", "pan_left", "pan_right", "tilt_up"]
            current_idx = motions.index(result.scenes[i].motion)
            result.scenes[i].motion = motions[(current_idx + 1) % len(motions)]

    # Save scene plan
    job_dir = get_job_dir(job_id)
    scenes_path = job_dir / "scene_plan.json"
    with open(scenes_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(
        "[%s] ✓ Scene plan complete — %d scenes, style='%s...' (provider: %s)",
        job_id,
        len(result.scenes),
        result.style_prefix[:40],
        llm_router.get_last_provider(),
    )
    return result
