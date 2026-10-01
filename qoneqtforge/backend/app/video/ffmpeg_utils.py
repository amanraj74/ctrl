"""FFmpeg utility wrappers for video processing."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """Get the FFmpeg executable path."""
    path = shutil.which("ffmpeg")
    if path is None:
        raise RuntimeError("FFmpeg not found. Install FFmpeg and ensure it's on PATH.")
    return path


def get_ffprobe_path() -> str:
    """Get the FFprobe executable path."""
    path = shutil.which("ffprobe")
    if path is None:
        raise RuntimeError("FFprobe not found. Install FFmpeg and ensure it's on PATH.")
    return path


def run_ffmpeg(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """Run an FFmpeg command with error handling."""
    cmd = [get_ffmpeg_path()] + args
    logger.debug("FFmpeg command: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error("FFmpeg stderr: %s", result.stderr[-500:] if result.stderr else "no stderr")
            raise RuntimeError(f"FFmpeg failed (code {result.returncode}): {result.stderr[-200:]}")
        return result

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"FFmpeg timed out after {timeout}s") from e


def run_ffprobe(args: list[str]) -> str:
    """Run an FFprobe command and return stdout."""
    cmd = [get_ffprobe_path()] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe failed: {result.stderr[:200]}")
    return result.stdout


def get_media_duration(file_path: str | Path) -> float:
    """Get the duration of a media file in seconds."""
    output = run_ffprobe([
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ])
    return float(output.strip())


def get_video_info(file_path: str | Path) -> dict:
    """Get video file information (resolution, fps, duration, etc.)."""
    import json as json_mod

    output = run_ffprobe([
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name",
        "-show_entries", "format=duration,size",
        "-of", "json",
        str(file_path),
    ])

    data = json_mod.loads(output)
    stream = data.get("streams", [{}])[0]
    fmt = data.get("format", {})

    # Parse frame rate (e.g., "30/1" -> 30.0)
    fps_str = stream.get("r_frame_rate", "30/1")
    if "/" in fps_str:
        num, den = fps_str.split("/")
        fps = float(num) / float(den)
    else:
        fps = float(fps_str)

    return {
        "width": stream.get("width", 0),
        "height": stream.get("height", 0),
        "fps": round(fps, 2),
        "codec": stream.get("codec_name", "unknown"),
        "duration": float(fmt.get("duration", 0)),
        "size_bytes": int(fmt.get("size", 0)),
    }


def has_audio_stream(file_path: str | Path) -> bool:
    """Check if a media file has an audio stream."""
    output = run_ffprobe([
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ])
    return "audio" in output.lower()


def concat_audio_files(audio_paths: list[str | Path], output_path: str | Path) -> None:
    """Concatenate multiple audio files into one."""
    # Create concat file list
    list_path = Path(output_path).parent / "concat_list.txt"
    with open(list_path, "w") as f:
        for path in audio_paths:
            f.write(f"file '{Path(path).resolve()}'\n")

    run_ffmpeg([
        "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_path),
        "-c", "copy",
        str(output_path),
    ])

    # Cleanup
    list_path.unlink(missing_ok=True)
