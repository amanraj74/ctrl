"""Stage 7: Voice — Synthesize narration audio with word-level timing."""

from __future__ import annotations

import json
import logging

from app.providers.tts_edge import EdgeTTSProvider
from app.providers.tts_piper import PiperTTSProvider
from app.schemas import BriefSpec, ScenePlan
from app.utils.paths import get_scene_audio_path, get_scene_timings_path

logger = logging.getLogger(__name__)


async def run(job_id: str, brief: BriefSpec, scene_plan: ScenePlan) -> list[dict]:
    """Synthesize voice narration for each scene.

    Returns list of dicts with audio paths, durations, and word timings.
    """
    logger.info("[%s] Stage 7: Voice — %d scenes, lang=%s", job_id, len(scene_plan.scenes), brief.language)

    # Try edge-tts first, then piper/pyttsx3
    tts_providers = [EdgeTTSProvider(), PiperTTSProvider()]
    tts_provider = None

    for provider in tts_providers:
        if await provider.is_available():
            tts_provider = provider
            break

    if tts_provider is None:
        raise RuntimeError("No TTS provider available")

    logger.info("[%s] Using TTS provider: %s", job_id, tts_provider.name)

    voice_results = []

    for scene in scene_plan.scenes:
        audio_path = get_scene_audio_path(job_id, scene.idx)
        timings_path = get_scene_timings_path(job_id, scene.idx)

        try:
            result = await tts_provider.synthesize(
                text=scene.narration,
                voice=brief.voice or "",
                output_path=audio_path,
                language=brief.language,
            )

            # Save word timings
            with open(timings_path, "w", encoding="utf-8") as f:
                json.dump(result.get("word_timings", []), f, indent=2)

            voice_results.append({
                "idx": scene.idx,
                "audio_path": str(audio_path),
                "timings_path": str(timings_path),
                "duration_sec": result.get("duration_sec", scene.duration_sec),
                "word_timings": result.get("word_timings", []),
                "provider": tts_provider.name,
                "success": True,
            })

            logger.info(
                "[%s] ✓ Scene %d voice: %.1fs",
                job_id,
                scene.idx,
                result.get("duration_sec", 0),
            )

        except Exception as e:
            logger.error("[%s] ✗ Scene %d voice failed: %s", job_id, scene.idx, e)
            voice_results.append({
                "idx": scene.idx,
                "success": False,
                "error": str(e),
                "duration_sec": scene.duration_sec,
            })

    total_duration = sum(r.get("duration_sec", 0) for r in voice_results)
    logger.info(
        "[%s] ✓ Voice complete — total duration: %.1fs, provider: %s",
        job_id,
        total_duration,
        tts_provider.name,
    )
    return voice_results
