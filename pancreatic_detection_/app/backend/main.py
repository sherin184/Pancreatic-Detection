from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.backend.gradcam import generate_gradcam
from app.backend.model_loader import get_model_info, load_model
from app.backend.predictor import predict_image_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "results" / "metrics" / "test_metrics.json"
logger = logging.getLogger(__name__)

app = FastAPI(title="Pancreatic Malignancy Detection API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_trained_model_on_startup() -> None:
    load_model()


@app.get("/")
def read_root() -> dict:
    return {
        "project": "Pancreatic Malignancy Detection",
        "status": "ready",
        "message": "Use /predict to upload an image for model analysis.",
    }


@app.get("/health")
def health_check() -> dict:
    model, device, _ = load_model()
    info = get_model_info()
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_available": model is not None,
        "model_path": info["model_path"],
        "device": str(device) if device else info["device"],
        "class_names": info["class_names"],
        "message": "Backend is running.",
    }


@app.get("/model-info")
def model_info() -> dict:
    return get_model_info()


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG or PNG.")

    file_bytes = await file.read()
    try:
        result = predict_image_bytes(file_bytes)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Prediction failed. Please try a different image.") from exc


@app.get("/metrics")
def get_metrics() -> dict:
    if not METRICS_PATH.exists():
        return {"status": "not_available", "message": "No evaluation metrics are available yet. Train and evaluate the model first."}

    with METRICS_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload["status"] = "available"
    return payload


@app.post("/gradcam")
async def gradcam(file: UploadFile = File(...)) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG or PNG.")

    file_bytes = await file.read()
    try:
        result = generate_gradcam(file_bytes)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        logger.exception("Grad-CAM generation failed")
        raise HTTPException(status_code=500, detail="Grad-CAM generation failed. Please try a different image.") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8003, reload=False)
