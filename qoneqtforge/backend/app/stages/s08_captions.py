"""Stage 8: Captions — Generate word-level ASS subtitles with karaoke highlight."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.utils.paths import get_captions_path, get_scene_timings_path

logger = logging.getLogger(__name__)


def _seconds_to_ass_time(seconds: float) -> str:
    """Convert seconds to ASS time format (H:MM:SS.cc)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _build_ass_header(font_name: str = "Poppins", font_size: int = 64) -> str:
    """Build the ASS subtitle file header."""
    return f"""[Script Info]
Title: QoneqtForge Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,400,1
Style: Active,{font_name},{font_size},&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _build_word_highlight_events(word_timings: list[dict], scene_offset: float = 0.0) -> list[str]:
    """Build ASS dialogue events with word-by-word karaoke highlight.

    Each word gets highlighted in yellow when spoken, white otherwise.
    """
    events = []

    for i, timing in enumerate(word_timings):
        start = timing["start"] + scene_offset
        end = timing["end"] + scene_offset
        word = timing["word"]

        # Build the line with current word highlighted
        # Use ASS override tags for karaoke effect
        start_time = _seconds_to_ass_time(start)
        end_time = _seconds_to_ass_time(end)

        # Simple approach: show each word as it's spoken with highlight
        event = f"Dialogue: 0,{start_time},{end_time},Active,,0,0,0,,{word}"
        events.append(event)

    return events


async def run(job_id: str, voice_results: list[dict]) -> str:
    """Generate ASS subtitles with word-level karaoke highlighting.

    Returns path to the generated .ass file.
    """
    logger.info("[%s] Stage 8: Captions — building word-level subtitles", job_id)

    # Collect all word timings across scenes
    all_timings = []
    scene_offset = 0.0

    for voice_result in voice_results:
        if not voice_result.get("success"):
            scene_offset += voice_result.get("duration_sec", 5.0)
            continue

        # Load word timings
        timings_path = voice_result.get("timings_path")
        word_timings = voice_result.get("word_timings", [])

        if not word_timings and timings_path and Path(timings_path).exists():
            with open(timings_path, "r", encoding="utf-8") as f:
                word_timings = json.load(f)

        # Add offset for scene position in the video
        for timing in word_timings:
            all_timings.append({
                "word": timing["word"],
                "start": timing["start"] + scene_offset,
                "end": timing["end"] + scene_offset,
                "duration": timing.get("duration", timing["end"] - timing["start"]),
            })

        scene_offset += voice_result.get("duration_sec", 5.0)

    # Build ASS file
    ass_content = _build_ass_header()

    # Group words into lines (max 5-6 words per line for readability)
    words_per_line = 5
    for i in range(0, len(all_timings), words_per_line):
        chunk = all_timings[i : i + words_per_line]
        if not chunk:
            continue

        line_start = _seconds_to_ass_time(chunk[0]["start"])
        line_end = _seconds_to_ass_time(chunk[-1]["end"])

        # Build line with karaoke timing
        # Use {\kf<duration>} for smooth fill
        karaoke_parts = []
        for timing in chunk:
            duration_cs = int(timing["duration"] * 100)
            word = timing["word"]
            karaoke_parts.append(f"{{\\kf{duration_cs}}}{word}")

        line_text = " ".join(karaoke_parts)
        event = f"Dialogue: 0,{line_start},{line_end},Default,,0,0,0,,{line_text}"
        ass_content += event + "\n"

    # Save ASS file
    captions_path = get_captions_path(job_id)
    captions_path.parent.mkdir(parents=True, exist_ok=True)
    with open(captions_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    logger.info(
        "[%s] ✓ Captions complete — %d words, saved to %s",
        job_id,
        len(all_timings),
        captions_path.name,
    )
    return str(captions_path)
