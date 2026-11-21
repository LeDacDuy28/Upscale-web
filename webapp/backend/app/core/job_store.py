"""Lightweight SQLite job metadata store shared between API and worker."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from .config import settings

DB_PATH = settings.STORAGE_DIR / "jobs.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                message TEXT,
                model TEXT NOT NULL,
                scale REAL NOT NULL,
                output_format TEXT NOT NULL,
                input_path TEXT NOT NULL,
                output_path TEXT,
                processing_time_ms INTEGER,
                error TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.commit()


def create_job(
    job_id: str,
    model: str,
    scale: float,
    output_format: str,
    input_path: Path,
) -> dict[str, Any]:
    now = time.time()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                job_id, status, progress, message, model, scale, output_format,
                input_path, created_at, updated_at
            ) VALUES (?, 'queued', 0, 'Queued', ?, ?, ?, ?, ?, ?)
            """,
            (job_id, model, scale, output_format, str(input_path), now, now),
        )
        conn.commit()
    return get_job(job_id)  # type: ignore[return-value]


def update_job(
    job_id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    message: Optional[str] = None,
    output_path: Optional[str] = None,
    processing_time_ms: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    fields: list[str] = ["updated_at = ?"]
    values: list[Any] = [time.time()]

    for col, val in (
        ("status", status),
        ("progress", progress),
        ("message", message),
        ("output_path", output_path),
        ("processing_time_ms", processing_time_ms),
        ("error", error),
    ):
        if val is not None:
            fields.append(f"{col} = ?")
            values.append(val)

    values.append(job_id)
    with _connect() as conn:
        conn.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE job_id = ?", values)
        conn.commit()


def get_job(job_id: str) -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def list_expired_jobs(cutoff_timestamp: float) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE created_at < ?", (cutoff_timestamp,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_job(job_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
        conn.commit()


init_db()
