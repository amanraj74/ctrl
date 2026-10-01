"""Stage 6: Visuals — Generate images for each scene using the image fallback chain."""

from __future__ import annotations

import asyncio
import logging

from app.providers.img_router import generate_image
from app.schemas import ScenePlan
from app.utils.paths import get_scene_image_path

logger = logging.getLogger(__name__)


async def _generate_scene_image(
    job_id: str,
    scene_idx: int,
    visual_prompt: str,
    style_prefix: str,
    stock_query: str | None,
) -> dict:
    """Generate image for a single scene."""
    try:
        image_bytes, provider = await generate_image(
            prompt=visual_prompt,
            style_prefix=style_prefix,
            stock_query=stock_query,
            seed=scene_idx * 42 + 7,
        )

        # Save image
        image_path = get_scene_image_path(job_id, scene_idx)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        logger.info(
            "[%s] ✓ Scene %d image: %d bytes via %s",
            job_id,
            scene_idx,
            len(image_bytes),
            provider,
        )
        return {
            "idx": scene_idx,
            "path": str(image_path),
            "provider": provider,
            "success": True,
        }

    except Exception as e:
        logger.error("[%s] ✗ Scene %d image failed: %s", job_id, scene_idx, e)
        return {
            "idx": scene_idx,
            "path": None,
            "provider": "none",
            "success": False,
            "error": str(e),
        }


async def run(job_id: str, scene_plan: ScenePlan) -> list[dict]:
    """Generate images for all scenes in parallel.

    Uses the image router's fallback chain for each scene.
    Never hard-fails — if a scene image fails, it's logged and the
    pipeline continues (compose will use a placeholder).
    """
    logger.info(
        "[%s] Stage 6: Visuals — generating %d scene images",
        job_id,
        len(scene_plan.scenes),
    )

    # Generate all scene images in parallel (with concurrency limit)
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent image generations

    async def _bounded_generate(scene) -> dict:
        async with semaphore:
            return await _generate_scene_image(
                job_id=job_id,
                scene_idx=scene.idx,
                visual_prompt=scene.visual_prompt,
                style_prefix=scene_plan.style_prefix,
                stock_query=scene.stock_query,
            )

    tasks = [_bounded_generate(scene) for scene in scene_plan.scenes]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    visual_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("[%s] Scene generation exception: %s", job_id, result)
            visual_results.append({"idx": -1, "success": False, "error": str(result)})
        else:
            visual_results.append(result)

    success_count = sum(1 for r in visual_results if r.get("success"))
    logger.info(
        "[%s] ✓ Visuals complete — %d/%d scenes generated",
        job_id,
        success_count,
        len(scene_plan.scenes),
    )
    return visual_results
