"""HTTP endpoints defining the Part B <-> Part C API contract (Section 3, Work item B1)."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.job_store import create_job, get_job
from app.core.validation import ALLOWED_FORMATS, generate_random_filename, validate_upload_bytes
from app.schemas.job import HealthStatus, JobInfo, ModelOption, UpscaleCreateResponse
from app.workers.worker import cleanup_expired_jobs, process_upscale_job
from serve.engine import MODEL_REGISTRY, list_available_models

router = APIRouter(prefix="/api", tags=["upscaler"])


def _enqueue_job(
    background_tasks: BackgroundTasks,
    job_id: str,
    input_path: Path,
    output_path: Path,
    model: str,
    scale: float,
    tile: int,
) -> None:
    if settings.USE_REDIS_QUEUE:
        try:
            from redis import Redis
            from rq import Queue

            redis_conn = Redis.from_url(settings.REDIS_URL)
            queue = Queue("upscale", connection=redis_conn)
            queue.enqueue(
                process_upscale_job,
                job_id,
                str(input_path),
                str(output_path),
                model,
                scale,
                tile,
                job_timeout="10m",
            )
            return
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Queue service unavailable: {exc}",
            ) from exc

    background_tasks.add_task(
        process_upscale_job,
        job_id,
        str(input_path),
        str(output_path),
        model,
        scale,
        tile,
    )


@router.get("/health", response_model=HealthStatus)
def health_check() -> HealthStatus:
    """Service liveness and GPU availability check."""
    gpu_available = False
    try:
        import torch

        gpu_available = bool(torch.cuda.is_available())
    except Exception:
        gpu_available = False

    mock_engine = os.getenv("USE_MOCK_ENGINE", "0").lower() in ("1", "true", "yes")
    return HealthStatus(
        status="ok",
        app_env=settings.APP_ENV,
        gpu_available=gpu_available,
        mock_engine=mock_engine,
    )


@router.get("/models", response_model=list[ModelOption])
def get_models() -> list[ModelOption]:
    """List supported Real-ESRGAN models and their available scales."""
    return [
        ModelOption(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            scales=item["scales"],
            default_tile=item["default_tile"],
            weights_available=item["weights_available"],
        )
        for item in list_available_models()
    ]


@router.post(
    "/upscale",
    response_model=UpscaleCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_upscale_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = Form("realesrgan_x4plus_student"),
    scale: int = Form(4),
    format: str = Form("png"),
) -> UpscaleCreateResponse:
    """Validate uploaded image, store safely, and enqueue upscale job."""
    cleanup_expired_jobs()

    if model not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model '{model}'.",
        )
    if scale not in MODEL_REGISTRY[model].scales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scale {scale} not supported for model '{model}'.",
        )

    out_fmt = format.lower().lstrip(".")
    if out_fmt == "jpeg":
        out_fmt = "jpg"
    if out_fmt not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported output format. Allowed: png, jpg, webp.",
        )

    raw_bytes = await file.read()
    detected_ext, _, _ = validate_upload_bytes(raw_bytes)

    job_id = uuid.uuid4().hex
    input_filename = generate_random_filename(detected_ext)
    output_filename = f"{job_id}.{out_fmt}"

    input_path = settings.STORAGE_DIR / "inputs" / input_filename
    output_path = settings.STORAGE_DIR / "outputs" / output_filename
    input_path.write_bytes(raw_bytes)

    create_job(
        job_id=job_id,
        model=model,
        scale=float(scale),
        output_format=out_fmt,
        input_path=input_path,
    )

    tile = MODEL_REGISTRY[model].default_tile or settings.DEFAULT_TILE_SIZE
    _enqueue_job(
        background_tasks=background_tasks,
        job_id=job_id,
        input_path=input_path,
        output_path=output_path,
        model=model,
        scale=float(scale),
        tile=tile,
    )

    return UpscaleCreateResponse(job_id=job_id)


@router.get("/jobs/{job_id}", response_model=JobInfo)
def get_job_status(job_id: str) -> JobInfo:
    """Fetch current job status, tile progress, and processing duration."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return JobInfo(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        message=job.get("message"),
        model=job["model"],
        scale=job["scale"],
        output_format=job["output_format"],
        processing_time_ms=job.get("processing_time_ms"),
        error=job.get("error"),
    )


@router.get("/jobs/{job_id}/result")
def download_job_result(job_id: str) -> FileResponse:
    """Download the upscaled image once the job status is 'done'."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if job["status"] != "done" or not job.get("output_path"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is not ready (status={job['status']}).",
        )
    out_path = Path(job["output_path"])
    if not out_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Result file has expired or been removed.",
        )

    ext = job["output_format"]
    media_map = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}
    return FileResponse(
        path=str(out_path),
        media_type=media_map.get(ext, "application/octet-stream"),
        filename=f"upscaled_{job_id}.{ext}",
    )
