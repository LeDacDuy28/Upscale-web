"""Background/RQ worker executing serve.engine.upscale with OOM tile fallback (B3, B4, B5)."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from app.core.config import settings
from app.core.job_store import delete_job, list_expired_jobs, update_job
from serve.engine import upscale

logger = logging.getLogger(__name__)


def _is_oom_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return "out of memory" in msg or "cuda error: out of memory" in msg


def process_upscale_job(
    job_id: str,
    input_path: str,
    output_path: str,
    model_name: str,
    scale: float,
    tile: int,
) -> dict:
    """Execute an upscale job, retrying with smaller tile sizes if CUDA OOM occurs."""
    update_job(job_id, status="processing", progress=5, message="Starting worker")

    # Build descending tile fallback candidates (e.g. [256, 128, 64])
    base_tile = tile if tile > 0 else settings.DEFAULT_TILE_SIZE
    tile_candidates = []
    for t in (base_tile, 256, 128, 64):
        if t <= base_tile and t not in tile_candidates:
            tile_candidates.append(t)
    if not tile_candidates:
        tile_candidates = [256, 128, 64]

    def _on_progress(pct: int, msg: str) -> None:
        update_job(job_id, progress=min(99, max(0, int(pct))), message=msg)

    last_error: BaseException | None = None
    for idx, current_tile in enumerate(tile_candidates):
        try:
            _, meta = upscale(
                image=input_path,
                output_path=output_path,
                model_name=model_name,
                scale=scale,
                tile=current_tile,
                fp16=settings.ENABLE_FP16,
                progress_callback=_on_progress,
            )
            update_job(
                job_id,
                status="done",
                progress=100,
                message="Completed",
                output_path=output_path,
                processing_time_ms=meta["processing_time_ms"],
            )
            return meta
        except RuntimeError as exc:
            last_error = exc
            if _is_oom_error(exc) and idx < len(tile_candidates) - 1:
                next_tile = tile_candidates[idx + 1]
                logger.warning(
                    "Job %s hit OOM at tile=%s, retrying with tile=%s",
                    job_id,
                    current_tile,
                    next_tile,
                )
                update_job(
                    job_id,
                    message=f"VRAM limit reached, retrying with tile={next_tile}",
                )
                try:
                    import torch

                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass
                continue
            break
        except Exception as exc:
            last_error = exc
            break

    error_msg = str(last_error) if last_error else "Unknown worker failure"
    logger.exception("Job %s failed: %s", job_id, error_msg)
    update_job(job_id, status="failed", message="Failed", error=error_msg)
    return {"error": error_msg}


def cleanup_expired_jobs(retention_seconds: int | None = None) -> int:
    """Remove uploaded/upscaled images and job records older than retention_seconds (B5)."""
    ttl = retention_seconds if retention_seconds is not None else settings.RETENTION_SECONDS
    cutoff = time.time() - ttl
    expired = list_expired_jobs(cutoff)
    removed = 0
    for job in expired:
        for key in ("input_path", "output_path"):
            p = job.get(key)
            if p and os.path.isfile(p):
                try:
                    Path(p).unlink(missing_ok=True)
                except OSError:
                    pass
        delete_job(job["job_id"])
        removed += 1
    return removed
