"""Pipeline Orchestrator — runs all 12 stages with quality gate loop, timing, and events."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone

from app.core.events import (
    emit_job_complete,
    emit_job_failed,
    emit_log,
    emit_stage_complete,
    emit_stage_start,
)
from app.db import get_session
from app.models import Job, LogLine, StageRun
from app.schemas import BriefSpec
from app.stages import (
    s01_ingest,
    s02_research,
    s03_script,
    s04_scenes,
    s05_critic,
    s06_visuals,
    s07_voice,
    s08_captions,
    s09_music,
    s10_compose,
    s11_qa,
    s12_export,
)

logger = logging.getLogger(__name__)

MAX_CRITIC_LOOPS = 2  # Max revision attempts from quality gate


def _log_and_emit(job_id: str, stage: str, level: str, message: str) -> None:
    """Log a message and emit it as an SSE event + save to DB."""
    getattr(logger, level)("[%s][%s] %s", job_id, stage, message)
    emit_log(job_id, stage, level, message)

    # Save to DB
    with get_session() as session:
        log_line = LogLine(
            job_id=job_id,
            stage_name=stage,
            level=level,
            message=message,
        )
        session.add(log_line)
        session.commit()


def _record_stage(
    job_id: str,
    stage_name: str,
    status: str,
    duration_ms: float,
    output: dict | None = None,
    error: str | None = None,
) -> None:
    """Record a stage run in the database."""
    with get_session() as session:
        stage_run = StageRun(
            job_id=job_id,
            stage_name=stage_name,
            status=status,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            output_json=json.dumps(output) if output else None,
            error=error,
        )
        session.add(stage_run)

        # Update job status
        job = session.get(Job, job_id)
        if job:
            job.current_stage = stage_name
            job.updated_at = datetime.now(timezone.utc)

        session.commit()


async def run_pipeline(job_id: str, brief: BriefSpec) -> None:
    """Run the full 12-stage pipeline for a job.

    Handles:
    - Stage sequencing
    - Quality gate revision loop (max 2 iterations)
    - Timing and logging per stage
    - SSE event emission
    - Error handling and recovery
    """
    logger.info("[%s] ═══ Pipeline started ═══", job_id)

    # Update job status to processing
    with get_session() as session:
        job = session.get(Job, job_id)
        if job:
            job.status = "processing"
            job.updated_at = datetime.now(timezone.utc)
            session.commit()

    pipeline_start = time.time()

    try:
        # ── Stage 1: Ingest ──
        emit_stage_start(job_id, "ingest")
        t = time.time()
        brief = await s01_ingest.run(job_id, brief)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "ingest", ms)
        _record_stage(job_id, "ingest", "completed", ms)
        _log_and_emit(job_id, "ingest", "info", f"✓ Completed in {ms:.0f}ms")

        # ── Stage 2: Research ──
        emit_stage_start(job_id, "research")
        t = time.time()
        research = await s02_research.run(job_id, brief)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "research", ms, {"fact_count": len(research.facts)})
        _record_stage(job_id, "research", "completed", ms)
        _log_and_emit(job_id, "research", "info", f"✓ {len(research.facts)} facts in {ms:.0f}ms")

        # ── Quality Gate Loop: Script → Scenes → Critic ──
        revision_feedback = None
        for loop_idx in range(MAX_CRITIC_LOOPS + 1):
            loop_label = f"(attempt {loop_idx + 1})" if loop_idx > 0 else ""

            # ── Stage 3: Script ──
            emit_stage_start(job_id, "script")
            t = time.time()
            script = await s03_script.run(job_id, brief, research, revision_feedback)
            ms = (time.time() - t) * 1000
            emit_stage_complete(job_id, "script", ms, {"hook": script.hook})
            _record_stage(job_id, "script", "completed", ms)
            _log_and_emit(job_id, "script", "info", f"✓ Script {loop_label} — hook='{script.hook}' {ms:.0f}ms")

            # ── Stage 4: Scene Plan ──
            emit_stage_start(job_id, "scenes")
            t = time.time()
            scene_plan = await s04_scenes.run(job_id, brief, script)
            ms = (time.time() - t) * 1000
            emit_stage_complete(job_id, "scenes", ms, {"scene_count": len(scene_plan.scenes)})
            _record_stage(job_id, "scenes", "completed", ms)
            _log_and_emit(job_id, "scenes", "info", f"✓ {len(scene_plan.scenes)} scenes {loop_label} {ms:.0f}ms")

            # ── Stage 5: Critic ──
            emit_stage_start(job_id, "critic")
            t = time.time()
            critic_report = await s05_critic.run(job_id, brief, script, scene_plan, research)
            ms = (time.time() - t) * 1000
            emit_stage_complete(job_id, "critic", ms, {
                "overall": critic_report.overall,
                "passed": critic_report.pass_,
                "scores": critic_report.scores,
            })
            _record_stage(job_id, "critic", "completed", ms)

            if critic_report.pass_:
                _log_and_emit(job_id, "critic", "info",
                              f"✓ PASSED — score {critic_report.overall:.1f}/10 {ms:.0f}ms")
                break
            else:
                _log_and_emit(job_id, "critic", "warning",
                              f"✗ FAILED — score {critic_report.overall:.1f}/10, revising... {ms:.0f}ms")
                if loop_idx < MAX_CRITIC_LOOPS:
                    revision_feedback = "\n".join(critic_report.must_fix)
                else:
                    _log_and_emit(job_id, "critic", "warning",
                                  "Max revisions reached, proceeding with best version")

        # ── Stage 6: Visuals ──
        emit_stage_start(job_id, "visuals")
        t = time.time()
        visual_results = await s06_visuals.run(job_id, scene_plan)
        ms = (time.time() - t) * 1000
        success_count = sum(1 for r in visual_results if r.get("success"))
        emit_stage_complete(job_id, "visuals", ms, {"generated": success_count, "total": len(scene_plan.scenes)})
        _record_stage(job_id, "visuals", "completed", ms)
        _log_and_emit(job_id, "visuals", "info", f"✓ {success_count}/{len(scene_plan.scenes)} images in {ms:.0f}ms")

        # ── Stage 7: Voice ──
        emit_stage_start(job_id, "voice")
        t = time.time()
        voice_results = await s07_voice.run(job_id, brief, scene_plan)
        ms = (time.time() - t) * 1000
        total_voice_duration = sum(r.get("duration_sec", 0) for r in voice_results)
        emit_stage_complete(job_id, "voice", ms, {"duration_sec": total_voice_duration})
        _record_stage(job_id, "voice", "completed", ms)
        _log_and_emit(job_id, "voice", "info", f"✓ Voice {total_voice_duration:.1f}s in {ms:.0f}ms")

        # ── Stage 8: Captions ──
        emit_stage_start(job_id, "captions")
        t = time.time()
        captions_path = await s08_captions.run(job_id, voice_results)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "captions", ms)
        _record_stage(job_id, "captions", "completed", ms)
        _log_and_emit(job_id, "captions", "info", f"✓ Captions generated in {ms:.0f}ms")

        # ── Stage 9: Music ──
        emit_stage_start(job_id, "music")
        t = time.time()
        music_result = await s09_music.run(job_id, brief, total_voice_duration)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "music", ms)
        _record_stage(job_id, "music", "completed", ms)
        _log_and_emit(job_id, "music", "info", f"✓ Music selected in {ms:.0f}ms")

        # ── Stage 10: Compose ──
        emit_stage_start(job_id, "compose")
        t = time.time()
        video_path = await s10_compose.run(
            job_id, script, scene_plan, voice_results, captions_path, music_result
        )
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "compose", ms)
        _record_stage(job_id, "compose", "completed", ms)
        _log_and_emit(job_id, "compose", "info", f"✓ Video composed in {ms:.0f}ms")

        # ── Stage 11: QA ──
        emit_stage_start(job_id, "qa")
        t = time.time()
        qa_report = await s11_qa.run(job_id, video_path, brief.duration_sec)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "qa", ms, {
            "all_passed": qa_report.all_passed,
            "checks": [c.model_dump() for c in qa_report.checks],
        })
        _record_stage(job_id, "qa", "completed", ms)
        status = "ALL PASSED" if qa_report.all_passed else "SOME FAILED"
        _log_and_emit(job_id, "qa", "info", f"✓ QA {status} in {ms:.0f}ms")

        # ── Stage 12: Export ──
        emit_stage_start(job_id, "export")
        t = time.time()
        export_pack = await s12_export.run(job_id, script, video_path)
        ms = (time.time() - t) * 1000
        emit_stage_complete(job_id, "export", ms)
        _record_stage(job_id, "export", "completed", ms)
        _log_and_emit(job_id, "export", "info", f"✓ Export pack created in {ms:.0f}ms")

        # ── Pipeline complete ──
        total_ms = (time.time() - pipeline_start) * 1000
        _log_and_emit(job_id, "pipeline", "info", f"═══ Pipeline complete in {total_ms/1000:.1f}s ═══")

        # Update job as completed
        with get_session() as session:
            job = session.get(Job, job_id)
            if job:
                job.status = "completed"
                job.video_path = video_path
                job.current_stage = None
                job.updated_at = datetime.now(timezone.utc)
                session.commit()

        emit_job_complete(job_id, f"/api/jobs/{job_id}/export.zip")

    except Exception as e:
        logger.exception("[%s] Pipeline failed: %s", job_id, e)

        with get_session() as session:
            job = session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                job.updated_at = datetime.now(timezone.utc)
                session.commit()

        emit_job_failed(job_id, str(e))
        raise
