"""Unit and integration tests for Backend API & upload validation (Work item B7)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import cv2
import numpy as np
from fastapi.testclient import TestClient

os.environ.setdefault("USE_MOCK_ENGINE", "1")
os.environ.setdefault("USE_REDIS_QUEUE", "false")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


def test_models_endpoint():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    models = resp.json()
    ids = {m["id"] for m in models}
    assert "realesrgan_x4plus_student" in ids
    assert "realesrgan_x4plus_teacher" in ids


def test_reject_invalid_magic_bytes():
    resp = client.post(
        "/api/upscale",
        files={"file": ("fake.png", b"not-an-image-payload", "image/png")},
        data={"model": "realesrgan_x4plus_student", "scale": "4", "format": "png"},
    )
    assert resp.status_code == 400


def test_end_to_end_upscale_mock():
    img = np.zeros((16, 16, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", img)
    assert ok

    create_resp = client.post(
        "/api/upscale",
        files={"file": ("sample.png", encoded.tobytes(), "image/png")},
        data={"model": "realesrgan_x4plus_student", "scale": "2", "format": "png"},
    )
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]

    status_resp = client.get(f"/api/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "done"

    result_resp = client.get(f"/api/jobs/{job_id}/result")
    assert result_resp.status_code == 200
    assert result_resp.headers["content-type"] == "image/png"
