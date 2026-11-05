from __future__ import annotations

from io import BytesIO

import numpy as np
import torch
from PIL import Image

from app.backend.model_loader import get_class_names, load_model
from src.preprocessing import build_eval_transform


def preprocess_image_bytes(file_bytes: bytes) -> torch.Tensor:
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    transform = build_eval_transform()
    tensor = transform(image)
    return tensor.unsqueeze(0)


def predict_image_bytes(file_bytes: bytes) -> dict:
    model, device, config = load_model()
    if model is None or device is None:
        raise RuntimeError("Trained model not available. Train the model first.")

    tensor = preprocess_image_bytes(file_bytes).to(device)
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]

    class_names = get_class_names()
    pred_index = int(np.argmax(probabilities))
    pred_label = class_names[pred_index]
    confidence = float(probabilities[pred_index])
    normal_probability = float(probabilities[0])
    pancreatic_tumour_probability = float(probabilities[1])
    probs = {class_names[0]: normal_probability, class_names[1]: pancreatic_tumour_probability}

    return {
        "prediction": pred_label,
        "predicted_class": pred_label,
        "confidence": confidence,
        "probabilities": probs,
        "normal_probability": normal_probability,
        "pancreatic_tumour_probability": pancreatic_tumour_probability,
        "model_name": config.get("model_name") if config else "ResNet50 + CBAM",
        "device": str(device),
    }
