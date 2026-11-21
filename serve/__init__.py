"""Shared model inference engine for RealESRGAN_Degradation_KD."""

from .engine import MODEL_REGISTRY, list_available_models, upscale

__all__ = ["MODEL_REGISTRY", "list_available_models", "upscale"]
