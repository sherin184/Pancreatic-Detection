from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class PredictionResult(BaseModel):
    prediction: str = Field(..., description="Predicted class label")
    predicted_class: str = Field(..., description="Predicted class label")
    confidence: float = Field(..., description="Predicted confidence for the winning class")
    probabilities: Dict[str, float] = Field(default_factory=dict)
    normal_probability: float
    pancreatic_tumour_probability: float


class GradCAMResult(BaseModel):
    prediction: str = Field(..., description="Predicted class label")
    confidence: float = Field(..., description="Predicted confidence for the winning class")
    original_image: str = Field(..., description="Original image encoded as base64")
    heatmap_image: str = Field(..., description="Grad-CAM heatmap encoded as base64")
    overlay_image: str = Field(..., description="Overlay image encoded as base64")


class ModelInfo(BaseModel):
    model_loaded: bool
    model_available: bool
    model_path: str | None = None
    load_error: str | None = None
    model_name: str | None = None
    device: str | None = None
    class_mapping: Dict[str, int] | None = None
    class_names: list[str] | None = None
    input_size: int | None = None
