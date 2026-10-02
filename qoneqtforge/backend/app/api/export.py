"""Export API — download the export pack ZIP."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.db import get_session
from app.models import Job
from app.utils.paths import get_job_dir

router = APIRouter(prefix="/api/jobs", tags=["export"])


@router.get("/{job_id}/export.zip")
async def download_export(job_id: str):
    """Download the export pack as a ZIP file."""
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")

    zip_path = get_job_dir(job_id) / "export.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Export pack not found")

    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"qoneqtforge_{job_id[:8]}_export.zip",
    )
