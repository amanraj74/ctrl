"""Audio mixing — ducking music under voice, loudness normalization."""

from __future__ import annotations

import logging
from pathlib import Path

from app.video.ffmpeg_utils import run_ffmpeg

logger = logging.getLogger(__name__)


def duck_music_under_voice(
    voice_path: str | Path,
    music_path: str | Path,
    output_path: str | Path,
    voice_volume: float = 1.0,
    music_volume: float = 0.15,
    target_lufs: float = -14.0,
) -> None:
    """Mix voice and music with ducking — music volume drops when voice is present.

    Uses FFmpeg amix + loudnorm for broadcast-quality audio.
    """
    logger.info("Audio mix: voice=%s, music=%s", Path(voice_path).name, Path(music_path).name)

    run_ffmpeg([
        "-y",
        "-i", str(voice_path),
        "-i", str(music_path),
        "-filter_complex",
        f"[0:a]volume={voice_volume}[voice];"
        f"[1:a]volume={music_volume}[music];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
        f"[mixed]loudnorm=I={target_lufs}:TP=-1.5:LRA=11[out]",
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ])

    logger.info("✓ Audio mixed: %s", Path(output_path).name)


def normalize_audio(
    input_path: str | Path,
    output_path: str | Path,
    target_lufs: float = -14.0,
) -> None:
    """Normalize audio loudness to target LUFS (EBU R128)."""
    run_ffmpeg([
        "-y",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ])
