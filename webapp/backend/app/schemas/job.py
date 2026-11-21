"""API contract schemas matching Section 3 of PROJECT_PLAN.md."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class UpscaleCreateResponse(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.queued


class JobInfo(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None
    model: str
    scale: float
    output_format: str
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class ModelOption(BaseModel):
    id: str
    name: str
    description: str
    scales: list[int]
    default_tile: int
    weights_available: bool


class HealthStatus(BaseModel):
    status: str
    app_env: str
    gpu_available: bool
    mock_engine: bool
