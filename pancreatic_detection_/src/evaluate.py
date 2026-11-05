from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import torch
from torch import nn

from src.dataset import CLASS_NAMES, build_dataloaders, prepare_dataset_splits
from src.models import build_resnet50_model, get_device
from src.train import (
    compute_binary_metrics,
    evaluate_model,
    plot_confusion_matrix,
    plot_roc_curve,
    save_test_evaluation,
)

MODEL_PATH = PROJECT_ROOT / "models" / "best_resnet50.pth"
MODEL_ALIAS_PATH = PROJECT_ROOT / "models" / "best_model.pth"


def load_best_model(model_path: Path | None = None):
    candidate_paths = [model_path] if model_path is not None else [MODEL_PATH, MODEL_ALIAS_PATH]
    resolved = next((path for path in candidate_paths if path is not None and path.exists()), None)
    if resolved is None:
        raise FileNotFoundError(
            "Saved model not found. Train the model first with 'python src\\train.py'."
        )

    device = get_device()
    checkpoint = torch.load(resolved, map_location=device)
    config = checkpoint.get("config", {})

    model = build_resnet50_model(num_classes=2, pretrained=False, freeze_backbone=False, use_cbam=True)
    model.load_state_dict(checkpoint["model_state"], strict=False)
    model.to(device)
    model.eval()
    return model, device, config


def main():
    train_paths, train_labels, val_paths, val_labels, test_paths, test_labels = prepare_dataset_splits()
    train_loader, val_loader, test_loader = build_dataloaders(
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
        batch_size=16,
    )

    model, device, config = load_best_model(MODEL_PATH)
    criterion = nn.CrossEntropyLoss()

    test_loss, test_acc, true_labels, probs, preds = evaluate_model(model, test_loader, criterion, device)
    metrics = compute_binary_metrics(true_labels, preds, probs)
    cm = plot_confusion_matrix(true_labels, preds)
    plot_roc_curve(true_labels, probs)

    prediction_rows = []
    for idx, file_path in enumerate(test_loader.dataset.file_paths):
        prediction_rows.append(
            {
                "image_name": Path(file_path).name,
                "true_label": CLASS_NAMES[int(test_labels[idx])],
                "predicted_label": CLASS_NAMES[int(preds[idx])],
                "normal_probability": float(probs[idx, 0]),
                "tumour_probability": float(probs[idx, 1]),
            }
        )

    save_test_evaluation(metrics, cm, prediction_rows)
    print("Evaluation complete. Results saved to results/metrics/ and results/figures/.")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")


if __name__ == "__main__":
    main()
