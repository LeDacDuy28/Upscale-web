"""Safe upload validation using magic bytes, size, and pixel limits (Work item B2)."""

from __future__ import annotations

import uuid
from typing import Tuple

import cv2
import numpy as np
from fastapi import HTTPException, status

from .config import settings

ALLOWED_FORMATS = {"png", "jpg", "jpeg", "webp"}


def detect_image_format_by_magic(data: bytes) -> str | None:
    """Inspect magic bytes instead of trusting the file extension."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def validate_upload_bytes(data: bytes) -> Tuple[str, int, int]:
    """Validate uploaded image bytes for format, file size, and resolution.

    Returns `(detected_ext, width, height)`.
    """
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit.",
        )

    detected_ext = detect_image_format_by_magic(data)
    if detected_ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file content. Allowed formats: PNG, JPG, WebP.",
        )

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or unreadable image file.",
        )

    height, width = img.shape[:2]
    if max(width, height) > settings.MAX_IMAGE_DIM:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image dimension {width}x{height} exceeds max {settings.MAX_IMAGE_DIM}px.",
        )

    return detected_ext, width, height


def generate_random_filename(ext: str) -> str:
    """Return a randomized filename to avoid path traversal and collisions."""
    clean_ext = ext.lower().lstrip(".")
    if clean_ext == "jpeg":
        clean_ext = "jpg"
    if clean_ext not in ALLOWED_FORMATS:
        clean_ext = "png"
    return f"{uuid.uuid4().hex}.{clean_ext}"
