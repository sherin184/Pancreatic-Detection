from __future__ import annotations

import base64
import logging
from io import BytesIO

import cv2
import numpy as np
import torch
from PIL import Image

from app.backend.model_loader import get_class_names, load_model
from src.preprocessing import build_eval_transform

logger = logging.getLogger(__name__)

try:
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
    from pytorch_grad_cam.utils.image import show_cam_on_image
except Exception:  # pragma: no cover
    GradCAM = None


def encode_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _create_fallback_heatmap(image: Image.Image) -> Image.Image:
    np_image = np.array(image.convert("RGB")).astype(np.float32)
    gray = np.mean(np_image, axis=2)
    heatmap = ((gray - gray.min()) / (gray.max() - gray.min() + 1e-8)) * 255
    heatmap = np.uint8(heatmap)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(np_image.astype(np.uint8), 0.65, heatmap_color, 0.35, 0)
    return Image.fromarray(overlay[..., ::-1])


def generate_gradcam(file_bytes: bytes) -> dict:
    model, device, config = load_model()
    if model is None or device is None:
        raise RuntimeError("Trained model not available. Train the model first.")

    original = Image.open(BytesIO(file_bytes)).convert("RGB")
    orig_w, orig_h = original.size
    input_tensor = build_eval_transform()(original).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(input_tensor)
        pred_index = int(torch.argmax(logits, dim=1).item())

    class_names = get_class_names()
    prediction_label = class_names[pred_index]
    confidence = float(torch.softmax(logits, dim=1)[0, pred_index].item())

    if GradCAM is not None:
        model.eval()
        target_layer = model.model.layer4[-1]
        targets = [ClassifierOutputTarget(pred_index)]
        with GradCAM(model=model, target_layers=[target_layer]) as cam:
            with torch.enable_grad():
                grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]
        grayscale_cam = np.maximum(grayscale_cam, 0)
        grayscale_cam = cv2.resize(grayscale_cam, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        cam_min = grayscale_cam.min()
        cam_max = grayscale_cam.max()
        cam_n = (grayscale_cam - cam_min) / (cam_max - cam_min + 1e-8)
        cam_n = np.nan_to_num(cam_n, nan=0.0, posinf=0.0, neginf=0.0)
        hotspot_y, hotspot_x = np.unravel_index(np.argmax(cam_n), cam_n.shape)
        logger.info("Grad-CAM hotspot in original-image coordinates: (x=%s, y=%s)", hotspot_x, hotspot_y)
        heatmap = np.uint8(255 * cam_n)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        image_rgb = np.array(original)
        image_float = image_rgb.astype(np.float32) / 255.0
        overlay = show_cam_on_image(image_float, cam_n, use_rgb=True)
        heatmap_image = Image.fromarray(heatmap_color[..., ::-1])
        overlay_image = Image.fromarray(overlay)
    else:
        heatmap_image = _create_fallback_heatmap(original)
        overlay_image = heatmap_image

    original_shape = np.array(original).shape
    heatmap_shape = np.array(heatmap_image).shape
    overlay_shape = np.array(overlay_image).shape
    logger.info(
        "Grad-CAM output shapes: original=%s, heatmap=%s, overlay=%s",
        original_shape,
        heatmap_shape,
        overlay_shape,
    )

    return {
        "prediction": prediction_label,
        "confidence": confidence,
        "original_image": encode_image_to_base64(original),
        "heatmap_image": encode_image_to_base64(heatmap_image),
        "overlay_image": encode_image_to_base64(overlay_image),
    }
