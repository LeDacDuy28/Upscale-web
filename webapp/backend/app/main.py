"""FastAPI application entrypoint for Real-ESRGAN Web Upscaler."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as upscale_router
from app.core.config import settings

app = FastAPI(
    title="Real-ESRGAN Degradation + KD Upscaler API",
    version="0.1.0",
    description="API contract for image upscaling with Real-ESRGAN Teacher & Student KD models.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upscale_router)
