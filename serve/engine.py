"""Shared inference engine wrapping RealESRGANer (Work item A14).

Supports:
- RealESRGAN_x4plus Student (KD: RRDBNet 48/16/24)
- RealESRGAN_x4plus Teacher (Fine-tuned: RRDBNet 64/23/32)
- RealESRGAN_x4plus Original (Baseline: RRDBNet 64/23/32)
- Grayscale, RGB, RGBA (alpha channel), and 16-bit images
- Deterministic mock fallback when USE_MOCK_ENGINE=1 or weights are not yet downloaded
"""

from __future__ import annotations

import logging
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, Union

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_ROOT = REPO_ROOT / "research"
BASICSR_ROOT = RESEARCH_ROOT / "BasicSR"
REALESRGAN_ROOT = RESEARCH_ROOT / "Real-ESRGAN"
MODELS_ROOT = Path(os.getenv("MODELS_DIR", str(RESEARCH_ROOT / "models")))

for _p in (str(BASICSR_ROOT), str(REALESRGAN_ROOT)):
    if _p not in sys.path and Path(_p).exists():
        sys.path.insert(0, _p)


@dataclass(frozen=True)
class ModelSpec:
    id: str
    name: str
    description: str
    scales: tuple[int, ...]
    num_feat: int
    num_block: int
    num_grow_ch: int
    netscale: int
    weight_relpath: str
    default_tile: int = 256


MODEL_REGISTRY: dict[str, ModelSpec] = {
    "realesrgan_x4plus_student": ModelSpec(
        id="realesrgan_x4plus_student",
        name="Real-ESRGAN x4+ Student (KD)",
        description="Model nhẹ được chưng cất tri thức (RRDBNet 48/16/24) từ teacher, tối ưu tốc độ.",
        scales=(2, 4),
        num_feat=48,
        num_block=16,
        num_grow_ch=24,
        netscale=4,
        weight_relpath="realesrgan_x4plus_student/v1/net_g_ema.pth",
        default_tile=256,
    ),
    "realesrgan_x4plus_teacher": ModelSpec(
        id="realesrgan_x4plus_teacher",
        name="Real-ESRGAN x4+ Teacher (Degradation)",
        description="Model teacher fine-tune với degradation nâng cao (RRDBNet 64/23/32).",
        scales=(2, 4),
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        netscale=4,
        weight_relpath="realesrgan_x4plus_teacher/v1/net_g_ema.pth",
        default_tile=256,
    ),
    "realesrgan_x4plus_original": ModelSpec(
        id="realesrgan_x4plus_original",
        name="Real-ESRGAN x4+ Original (Baseline)",
        description="Model RealESRGAN_x4plus gốc dùng để đối chiếu baseline.",
        scales=(2, 4),
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        netscale=4,
        weight_relpath="realesrgan_x4plus_original/v1/RealESRGAN_x4plus.pth",
        default_tile=256,
    ),
}

ProgressCallback = Callable[[int, str], None]


def list_available_models() -> list[dict]:
    """Return metadata for all registered models including local weight availability."""
    models = []
    for spec in MODEL_REGISTRY.values():
        weight_path = MODELS_ROOT / spec.weight_relpath
        item = asdict(spec)
        item["scales"] = list(spec.scales)
        item["weights_available"] = weight_path.is_file()
        item["weight_path"] = str(weight_path)
        models.append(item)
    return models


class _ProgressReportingRealESRGANer:
    """Wrapper helper to attach tile progress reporting when RealESRGANer runs."""

    @staticmethod
    def build(spec: ModelSpec, weight_path: Path, tile: int, fp16: bool, gpu_id: Optional[int]):
        import torch
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        net = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=spec.num_feat,
            num_block=spec.num_block,
            num_grow_ch=spec.num_grow_ch,
            scale=spec.netscale,
        )
        use_half = fp16 and torch.cuda.is_available()
        return RealESRGANer(
            scale=spec.netscale,
            model_path=str(weight_path),
            model=net,
            tile=tile,
            tile_pad=10,
            pre_pad=0,
            half=use_half,
            gpu_id=gpu_id,
        )


def _mock_upscale(
    img: np.ndarray,
    scale: float,
    tile: int,
    progress_callback: Optional[ProgressCallback] = None,
) -> np.ndarray:
    """Fast deterministic fallback upscaler for local dev / CI without GPU weights."""
    import cv2

    h, w = img.shape[:2]
    target_w = max(1, int(round(w * scale)))
    target_h = max(1, int(round(h * scale)))

    steps = max(2, math.ceil(max(h, w) / max(tile, 256)))
    for idx in range(steps):
        if progress_callback:
            pct = min(90, int(((idx + 1) / steps) * 85) + 5)
            progress_callback(pct, f"Mock tile {idx + 1}/{steps}")
        time.sleep(0.05)

    return cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_CUBIC)


def _read_image(image: Union[str, Path, np.ndarray]) -> np.ndarray:
    import cv2
    import numpy as np

    if isinstance(image, np.ndarray):
        return image
    path = str(image)
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image from path: {path}")
    return img


def upscale(
    image: Union[str, Path, np.ndarray],
    output_path: Optional[Union[str, Path]] = None,
    model_name: str = "realesrgan_x4plus_student",
    scale: float = 4.0,
    tile: int = 256,
    fp16: bool = True,
    gpu_id: Optional[int] = None,
    progress_callback: Optional[ProgressCallback] = None,
) -> tuple[np.ndarray, dict]:
    """Upscale an image using the selected model.

    Handles grayscale, RGB, RGBA (alpha preserved), and 16-bit images.
    Returns `(output_array, metadata_dict)`.
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_name}'. Available: {list(MODEL_REGISTRY.keys())}"
        )

    spec = MODEL_REGISTRY[model_name]
    if int(scale) not in spec.scales and float(scale) not in spec.scales:
        raise ValueError(f"Scale {scale} not supported by {model_name}. Supported: {spec.scales}")

    if progress_callback:
        progress_callback(5, "Loading image")

    img = _read_image(image)
    h_in, w_in = img.shape[:2]
    weight_path = MODELS_ROOT / spec.weight_relpath
    force_mock = os.getenv("USE_MOCK_ENGINE", "0").lower() in ("1", "true", "yes")

    t0 = time.perf_counter()
    used_mock = False

    if force_mock or not weight_path.is_file():
        if not force_mock:
            logger.warning(
                "Weight file '%s' not found; falling back to mock bicubic upscale. "
                "Place trained .pth weights in research/models/ to run neural inference.",
                weight_path,
            )
        used_mock = True
        output = _mock_upscale(img, scale=scale, tile=tile, progress_callback=progress_callback)
    else:
        if progress_callback:
            progress_callback(15, f"Loading model {spec.name}")
        upsampler = _ProgressReportingRealESRGANer.build(
            spec=spec,
            weight_path=weight_path,
            tile=tile,
            fp16=fp16,
            gpu_id=gpu_id,
        )
        if progress_callback:
            progress_callback(35, "Running RealESRGANer inference")
        output, _ = upsampler.enhance(img, outscale=scale)

    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    if output_path is not None:
        import cv2

        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        ok = cv2.imwrite(str(out_p), output)
        if not ok:
            raise IOError(f"Failed to write output image to {out_p}")

    if progress_callback:
        progress_callback(100, "Done")

    h_out, w_out = output.shape[:2]
    meta = {
        "model": model_name,
        "scale": scale,
        "tile": tile,
        "mock": used_mock,
        "input_size": [w_in, h_in],
        "output_size": [w_out, h_out],
        "processing_time_ms": elapsed_ms,
    }
    return output, meta
