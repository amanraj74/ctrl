"""ASS caption/subtitle builder with word-level karaoke highlighting."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_ass_file(
    word_timings: list[dict],
    font_name: str = "Poppins",
    font_size: int = 64,
    primary_color: str = "&H00FFFFFF",  # White
    highlight_color: str = "&H0000FFFF",  # Yellow
    outline_color: str = "&H00000000",  # Black
    outline_width: int = 4,
    margin_v: int = 400,  # Bottom margin (safe zone)
) -> str:
    """Build an ASS subtitle file with word-level karaoke highlighting.

    Args:
        word_timings: List of dicts with word, start, end, duration
        font_name: Font family name
        font_size: Font size in pixels
        primary_color: Default text color (ASS format &HAABBGGRR)
        highlight_color: Active word color
        outline_color: Text outline color
        outline_width: Outline thickness
        margin_v: Vertical margin from bottom

    Returns:
        Complete ASS file content as string
    """
    header = f"""[Script Info]
Title: QoneqtForge Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},{highlight_color},{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,{outline_width},2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    words_per_line = 5

    for i in range(0, len(word_timings), words_per_line):
        chunk = word_timings[i : i + words_per_line]
        if not chunk:
            continue

        start = _seconds_to_ass(chunk[0]["start"])
        end = _seconds_to_ass(chunk[-1]["end"])

        # Build karaoke line
        parts = []
        for t in chunk:
            dur_cs = max(1, int(t["duration"] * 100))
            parts.append(f"{{\\kf{dur_cs}}}{t['word']}")

        text = " ".join(parts)
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    return header + "\n".join(events) + "\n"


def _seconds_to_ass(seconds: float) -> str:
    """Convert seconds to ASS timestamp format H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
