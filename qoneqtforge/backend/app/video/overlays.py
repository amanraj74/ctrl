"""Video overlays — hook text, watermark, end card."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_hook_text_filter(
    hook_text: str,
    duration: float = 2.5,
    font_size: int = 80,
    font_color: str = "white",
    font_name: str = "Poppins",
) -> str:
    """Generate FFmpeg drawtext filter for the hook text overlay.

    Shows large, bold text in the first few seconds to grab attention.
    """
    # Escape special characters for FFmpeg
    escaped = hook_text.replace("'", "\\'").replace(":", "\\:")

    return (
        f"drawtext=text='{escaped}'"
        f":fontfile=assets/fonts/Poppins-Bold.ttf"
        f":fontsize={font_size}"
        f":fontcolor={font_color}"
        f":borderw=4:bordercolor=black"
        f":x=(w-text_w)/2:y=(h-text_h)/2"
        f":enable='between(t,0.3,{duration})'"
        f":alpha='if(lt(t,0.5),t/0.5,if(gt(t,{duration-0.3}),(({duration}-t)/0.3),1))'"
    )


def get_watermark_filter(
    watermark_path: str = "assets/brand/watermark.png",
    opacity: float = 0.5,
    margin: int = 20,
) -> str:
    """Generate FFmpeg overlay filter for watermark.

    Places a semi-transparent watermark in the top-right corner.
    """
    return (
        f"movie={watermark_path}[wm];"
        f"[in][wm]overlay=W-overlay_w-{margin}:{margin}:format=auto:alpha={opacity}[out]"
    )


def get_end_card_text(
    text: str = "Join the conversation on Qoneqt",
    duration: float = 1.5,
    total_duration: float = 30.0,
    font_size: int = 56,
) -> str:
    """Generate FFmpeg drawtext filter for the end card.

    Shows CTA text in the last few seconds of the video.
    """
    start_time = total_duration - duration
    escaped = text.replace("'", "\\'").replace(":", "\\:")

    return (
        f"drawtext=text='{escaped}'"
        f":fontsize={font_size}"
        f":fontcolor=white"
        f":borderw=3:bordercolor=black"
        f":x=(w-text_w)/2:y=(h-text_h)/2"
        f":enable='gte(t,{start_time})'"
    )
