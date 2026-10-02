"""Stage 10: Compose — Assemble all media into a final 1080×1920 MP4 video."""

from __future__ import annotations

import logging
from pathlib import Path

from app.schemas import ScenePlan, Script
from app.utils.paths import get_final_video_path, get_job_dir, get_scene_audio_path, get_scene_image_path
from app.video.ffmpeg_utils import run_ffmpeg
from app.video.kenburns import get_kenburns_filter

logger = logging.getLogger(__name__)

WIDTH = 1080
HEIGHT = 1920
FPS = 30


async def run(
    job_id: str,
    script: Script,
    scene_plan: ScenePlan,
    voice_results: list[dict],
    captions_path: str | None,
    music_result: dict,
) -> str:
    """Compose the final video from all pipeline outputs.

    Pipeline:
    1. For each scene: apply Ken Burns to image, set duration from TTS audio
    2. Concatenate scene clips
    3. Add voice-over audio
    4. Add background music (ducked)
    5. Burn captions (ASS subtitles)
    6. Apply loudness normalization

    Returns path to final.mp4
    """
    logger.info("[%s] Stage 10: Compose — assembling final video", job_id)

    job_dir = get_job_dir(job_id)
    final_path = get_final_video_path(job_id)
    final_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Create individual scene clips with Ken Burns
    scene_clips = []
    scene_audios = []
    total_duration = 0.0

    for i, scene in enumerate(scene_plan.scenes):
        image_path = get_scene_image_path(job_id, scene.idx)
        audio_path = get_scene_audio_path(job_id, scene.idx)

        if not image_path.exists():
            logger.warning("[%s] Scene %d image missing, skipping", job_id, scene.idx)
            continue

        # Get actual audio duration (prefer TTS duration over plan estimate)
        voice_info = next((v for v in voice_results if v.get("idx") == scene.idx), None)
        scene_duration = voice_info.get("duration_sec", scene.duration_sec) if voice_info else scene.duration_sec
        scene_duration += 0.3  # Add 0.3s tail padding
        scene_duration = max(2.0, scene_duration)  # Minimum 2 seconds

        # Create scene clip with Ken Burns effect
        scene_clip_path = job_dir / f"scene_{scene.idx}_clip.mp4"

        kb_filter = get_kenburns_filter(
            motion=scene.motion,
            duration_sec=scene_duration,
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
        )

        ffmpeg_args = [
            "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-vf", kb_filter,
            "-t", str(scene_duration),
            "-c:v", "libx264",
            "-crf", "22",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-r", str(FPS),
            str(scene_clip_path),
        ]

        try:
            run_ffmpeg(ffmpeg_args, timeout=120)
            scene_clips.append(str(scene_clip_path))
            total_duration += scene_duration
            logger.info("[%s] Scene %d clip: %.1fs", job_id, scene.idx, scene_duration)
        except Exception as e:
            logger.error("[%s] Scene %d clip failed: %s", job_id, scene.idx, e)

        # Collect audio
        if audio_path.exists():
            scene_audios.append(str(audio_path))

    if not scene_clips:
        raise RuntimeError("No scene clips were generated — cannot compose video")

    # Step 2: Concatenate scene clips
    concat_path = job_dir / "concat_video.mp4"
    concat_list = job_dir / "concat_list.txt"

    with open(concat_list, "w") as f:
        for clip in scene_clips:
            f.write(f"file '{Path(clip).resolve()}'\n")

    run_ffmpeg([
        "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concat_path),
    ])

    # Step 3: Concatenate audio
    voice_audio_path = job_dir / "voice_full.mp3"
    if scene_audios:
        audio_list = job_dir / "audio_list.txt"
        with open(audio_list, "w") as f:
            for audio in scene_audios:
                f.write(f"file '{Path(audio).resolve()}'\n")

        run_ffmpeg([
            "-y", "-f", "concat", "-safe", "0",
            "-i", str(audio_list),
            "-c", "copy",
            str(voice_audio_path),
        ])

    # Step 4: Combine video + audio + music + captions
    ffmpeg_final_args = ["-y"]

    # Input: concatenated video
    ffmpeg_final_args.extend(["-i", str(concat_path)])

    # Input: voice audio
    if voice_audio_path.exists():
        ffmpeg_final_args.extend(["-i", str(voice_audio_path)])

    # Input: music (optional)
    music_path = music_result.get("music_path") if music_result.get("success") else None
    if music_path and Path(music_path).exists():
        ffmpeg_final_args.extend(["-i", str(music_path)])

    # Build filter complex for audio mixing
    has_voice = voice_audio_path.exists()
    has_music = music_path and Path(music_path).exists()

    filter_parts = []
    if has_voice and has_music:
        # Mix voice + music with ducking
        filter_parts.append("[1:a]volume=1.0[voice]")
        filter_parts.append("[2:a]volume=0.12[music]")
        filter_parts.append("[voice][music]amix=inputs=2:duration=first:dropout_transition=2[mixed]")
        filter_parts.append("[mixed]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        audio_map = "[aout]"
    elif has_voice:
        filter_parts.append("[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        audio_map = "[aout]"
    else:
        audio_map = None

    # Add subtitle burn if available
    video_map = "0:v"
    if captions_path and Path(captions_path).exists():
        ass_escaped = str(Path(captions_path).resolve()).replace("\\", "/").replace(":", "\\:")
        if filter_parts:
            filter_parts.insert(0, f"[0:v]ass='{ass_escaped}'[vout]")
            video_map = "[vout]"
        else:
            ffmpeg_final_args.extend(["-vf", f"ass='{ass_escaped}'"])

    if filter_parts:
        ffmpeg_final_args.extend(["-filter_complex", ";".join(filter_parts)])

    # Output mapping
    ffmpeg_final_args.extend(["-map", video_map])
    if audio_map:
        ffmpeg_final_args.extend(["-map", audio_map])

    # Output settings
    ffmpeg_final_args.extend([
        "-c:v", "libx264",
        "-crf", "20",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(final_path),
    ])

    run_ffmpeg(ffmpeg_final_args, timeout=300)

    # Cleanup intermediate files
    for clip in scene_clips:
        Path(clip).unlink(missing_ok=True)
    concat_path.unlink(missing_ok=True)
    concat_list.unlink(missing_ok=True)

    logger.info(
        "[%s] ✓ Compose complete — %s (%.1fs total)",
        job_id,
        final_path.name,
        total_duration,
    )
    return str(final_path)
