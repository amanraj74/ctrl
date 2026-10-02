"""Stage 9: Music — Select and process background music track."""

from __future__ import annotations

import json
import logging
import random
import shutil

from app.config import settings
from app.schemas import BriefSpec
from app.utils.paths import get_music_path

logger = logging.getLogger(__name__)

# Mood to music mapping
TONE_MOOD_MAP = {
    "energetic": ["upbeat", "energetic", "motivational"],
    "calm": ["ambient", "chill", "relaxing"],
    "funny": ["playful", "upbeat", "quirky"],
    "inspiring": ["motivational", "uplifting", "cinematic"],
    "explainer": ["ambient", "neutral", "tech"],
}


def _load_music_catalog() -> list[dict]:
    """Load the music catalog from assets/music/music.json."""
    catalog_path = settings.music_dir / "music.json"
    if catalog_path.exists():
        with open(catalog_path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _select_track(tone: str, catalog: list[dict]) -> dict | None:
    """Select a track matching the tone/mood."""
    target_moods = TONE_MOOD_MAP.get(tone, ["ambient"])

    # Find tracks matching any target mood
    matching = [
        track for track in catalog if track.get("mood", "").lower() in target_moods
    ]

    if matching:
        return random.choice(matching)

    # Fallback: any track
    if catalog:
        return random.choice(catalog)

    return None


async def run(job_id: str, brief: BriefSpec, total_duration: float) -> dict:
    """Select and prepare background music for the video.

    Returns dict with music_path, track_info, and processing details.
    """
    logger.info("[%s] Stage 9: Music — tone=%s, duration=%.1fs", job_id, brief.tone, total_duration)

    music_path = get_music_path(job_id)
    music_path.parent.mkdir(parents=True, exist_ok=True)

    # Load music catalog
    catalog = _load_music_catalog()

    if catalog:
        track = _select_track(brief.tone, catalog)
        if track:
            source_path = settings.music_dir / track["filename"]
            if source_path.exists():
                # Copy track to job directory
                shutil.copy2(source_path, music_path)
                logger.info("[%s] ✓ Music selected: %s (mood: %s)", job_id, track["filename"], track.get("mood"))
                return {
                    "music_path": str(music_path),
                    "track": track,
                    "success": True,
                }

    # No music available — video will be voice-only
    logger.warning("[%s] No music tracks available — video will be voice-only", job_id)
    return {
        "music_path": None,
        "track": None,
        "success": False,
        "message": "No music tracks available. Add MP3 files to assets/music/",
    }
