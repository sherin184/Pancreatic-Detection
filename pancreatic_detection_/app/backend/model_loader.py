from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import traceback

import torch

from src.models import build_resnet50_model, get_device

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_CANDIDATES = [
    PROJECT_ROOT / "models" / "best_model.pth",
    PROJECT_ROOT / "models" / "best_resnet50.pth",
]
CLASS_NAMES = ["Normal", "Pancreatic Tumour"]
CLASS_MAPPING = {"Normal": 0, "Pancreatic Tumour": 1}
_last_model_path: Path | None = None
_last_load_error: str | None = None


@lru_cache(maxsize=1)
def load_model() -> tuple[Any | None, torch.device | None, dict[str, Any] | None]:
    """Load the trained model once and cache it for the backend lifetime."""
    global _last_model_path, _last_load_error

    model_path = next((path for path in MODEL_CANDIDATES if path.exists()), None)
    if model_path is None:
        _last_model_path = None
        _last_load_error = "No trained checkpoint was found in the models directory."
        print(f"Model path: {PROJECT_ROOT / 'models'}")
        print("Model loaded: False")
        print(f"Model load error: {_last_load_error}")
        return None, None, None

    _last_model_path = model_path
    try:
        device = get_device()
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        if not isinstance(checkpoint, dict) or "model_state" not in checkpoint:
            raise KeyError("Checkpoint does not contain the expected 'model_state' key.")

        config = checkpoint.get("config", {})
        model = build_resnet50_model(num_classes=2, pretrained=False, freeze_backbone=False, use_cbam=True)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.to(device)
        model.eval()

        _last_load_error = None
        print(f"Model path: {model_path}")
        print("Model loaded: True")
        print(f"Device: {device}")
        print(f"Classes: {CLASS_NAMES}")
        return model, device, config
    except Exception as exc:
        _last_load_error = str(exc)
        print(f"Model path: {model_path}")
        print("Model loaded: False")
        print("Complete model loading exception:")
        traceback.print_exc()
        return None, None, None


def get_class_names() -> list[str]:
    return CLASS_NAMES.copy()


def get_model_info() -> dict[str, Any]:
    model, device, config = load_model()
    return {
        "model_loaded": model is not None,
        "model_available": model is not None,
        "model_path": str(_last_model_path) if _last_model_path else None,
        "load_error": _last_load_error,
        "model_name": config.get("model_name") if config else "ResNet50 + CBAM",
        "device": str(device) if device else "cpu",
        "class_mapping": CLASS_MAPPING.copy(),
        "class_names": CLASS_NAMES.copy(),
        "input_size": config.get("input_size") if config else 224,
    }
