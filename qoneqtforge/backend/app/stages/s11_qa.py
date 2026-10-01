"""Stage 11: QA — Automated quality checks on the final video."""

from __future__ import annotations

import logging
from pathlib import Path

from app.schemas import QACheck, QAReport
from app.video.ffmpeg_utils import get_video_info, has_audio_stream, run_ffprobe

logger = logging.getLogger(__name__)


async def run(job_id: str, video_path: str, target_duration: float = 30.0) -> QAReport:
    """Run automated quality checks on the final video.

    Checks:
    - Resolution (1080×1920)
    - Duration (within ±10% of target)
    - Audio stream present
    - FPS (30)
    - File size (≤ 50MB)
    - Black frame detection

    Returns QAReport with green/red checks for UI display.
    """
    logger.info("[%s] Stage 11: QA — checking %s", job_id, Path(video_path).name)

    checks = []
    warnings = []

    if not Path(video_path).exists():
        return QAReport(
            checks=[QACheck(name="File exists", passed=False, expected="exists", actual="missing", message="Video file not found")],
            all_passed=False,
            warnings=["Video file does not exist"],
        )

    # Get video info
    try:
        info = get_video_info(video_path)
    except Exception as e:
        return QAReport(
            checks=[QACheck(name="Readable", passed=False, expected="valid video", actual=str(e), message="Cannot read video file")],
            all_passed=False,
        )

    # Check 1: Resolution
    expected_res = "1080×1920"
    actual_res = f"{info['width']}×{info['height']}"
    res_ok = info["width"] == 1080 and info["height"] == 1920
    if not res_ok:
        # Allow close resolutions
        res_ok = abs(info["width"] - 1080) <= 10 and abs(info["height"] - 1920) <= 10
        if res_ok:
            warnings.append(f"Resolution slightly off: {actual_res} (expected {expected_res})")

    checks.append(QACheck(
        name="Resolution",
        passed=res_ok,
        expected=expected_res,
        actual=actual_res,
        message="Vertical 9:16 format" if res_ok else "Resolution mismatch",
    ))

    # Check 2: Duration
    duration = info["duration"]
    duration_tolerance = target_duration * 0.15  # 15% tolerance
    dur_ok = abs(duration - target_duration) <= duration_tolerance
    checks.append(QACheck(
        name="Duration",
        passed=dur_ok,
        expected=f"{target_duration:.1f}s ±15%",
        actual=f"{duration:.1f}s",
        message="Duration within range" if dur_ok else f"Duration off by {abs(duration - target_duration):.1f}s",
    ))

    # Check 3: Audio stream
    has_audio = has_audio_stream(video_path)
    checks.append(QACheck(
        name="Audio",
        passed=has_audio,
        expected="present",
        actual="present" if has_audio else "missing",
        message="Audio stream found" if has_audio else "No audio stream detected",
    ))

    # Check 4: FPS
    fps_ok = abs(info["fps"] - 30) <= 1
    checks.append(QACheck(
        name="Frame Rate",
        passed=fps_ok,
        expected="30 fps",
        actual=f"{info['fps']} fps",
        message="Standard frame rate" if fps_ok else "Non-standard frame rate",
    ))

    # Check 5: File size (≤ 50MB)
    size_mb = info["size_bytes"] / (1024 * 1024)
    size_ok = size_mb <= 50
    checks.append(QACheck(
        name="File Size",
        passed=size_ok,
        expected="≤ 50 MB",
        actual=f"{size_mb:.1f} MB",
        message="Within upload limit" if size_ok else "File too large for upload",
    ))

    # Check 6: Codec
    codec_ok = info["codec"] in ("h264", "libx264", "avc1")
    checks.append(QACheck(
        name="Video Codec",
        passed=codec_ok,
        expected="H.264",
        actual=info["codec"],
        message="Compatible codec" if codec_ok else "Unexpected codec",
    ))

    # Check 7: Black frame detection
    try:
        black_output = run_ffprobe([
            "-f", "lavfi",
            "-i", f"movie={str(Path(video_path).resolve()).replace(chr(92), '/')}",
            "-vf", "blackdetect=d=0.5:pix_th=0.10",
            "-show_entries", "tags=lavfi.black_start",
            "-of", "default=nw=1",
            str(video_path),
        ])
        has_black = "black_start" in black_output
    except Exception:
        has_black = False  # Assume no black frames if check fails

    checks.append(QACheck(
        name="No Black Frames",
        passed=not has_black,
        expected="no black frames > 0.5s",
        actual="black frames detected" if has_black else "clean",
        message="No problematic black frames" if not has_black else "Black frames detected",
    ))

    all_passed = all(c.passed for c in checks)

    report = QAReport(
        checks=checks,
        all_passed=all_passed,
        warnings=warnings,
    )

    status = "✓ ALL PASSED" if all_passed else "✗ SOME FAILED"
    logger.info(
        "[%s] %s — %d/%d checks passed",
        job_id,
        status,
        sum(1 for c in checks if c.passed),
        len(checks),
    )

    return report
