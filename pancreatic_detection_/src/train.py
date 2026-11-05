from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from torch import nn
from torch.optim import AdamW

from src.dataset import (
    CLASS_NAMES,
    CLASS_TO_INDEX,
    BATCH_SIZE,
    RANDOM_SEED,
    verify_dataset_structure,
    build_dataloaders,
    compute_class_weights,
    prepare_dataset_splits,
)
from src.models import build_resnet50_model, get_device, print_system_info
from src.preprocessing import get_preprocessing_config

MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
METRICS_DIR = RESULTS_DIR / "metrics"
MODEL_PATH = MODELS_DIR / "best_resnet50.pth"
MODEL_ALIAS_PATH = MODELS_DIR / "best_model.pth"
TRAINING_CURVE_PATH = FIGURES_DIR / "training_curves.png"

# Tunable configuration
EPOCHS = 20
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
PATIENCE = 5
MIN_DELTA = 1e-4
FREEZE_BACKBONE = True
USE_MIXED_PRECISION = True
BATCH_SIZE = 16


def set_seed(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_one_epoch(model, loader, criterion, optimizer, device, scaler=None):
    model.train()
    running_loss = 0.0
    running_correct = 0
    total_items = 0

    for images, labels, _ in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with torch.autocast(device_type=device.type, enabled=(scaler is not None and device.type == "cuda")):
            logits = model(images)
            loss = criterion(logits, labels)

        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        preds = logits.argmax(dim=1)
        running_correct += (preds == labels).sum().item()
        total_items += labels.size(0)

    avg_loss = running_loss / max(total_items, 1)
    acc = running_correct / max(total_items, 1)
    return avg_loss, acc


def evaluate_model(model, loader, criterion, device, scaler=None):
    model.eval()
    running_loss = 0.0
    running_correct = 0
    total_items = 0
    all_labels = []
    all_probs = []
    all_preds = []

    with torch.no_grad():
        for images, labels, _ in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            with torch.autocast(device_type=device.type, enabled=(scaler is not None and device.type == "cuda")):
                logits = model(images)
                loss = criterion(logits, labels)

            probs = torch.softmax(logits, dim=1)
            preds = logits.argmax(dim=1)

            running_loss += loss.item() * images.size(0)
            running_correct += (preds == labels).sum().item()
            total_items += labels.size(0)

            all_labels.extend(labels.cpu().numpy().tolist())
            all_probs.extend(probs.cpu().numpy().tolist())
            all_preds.extend(preds.cpu().numpy().tolist())

    avg_loss = running_loss / max(total_items, 1)
    acc = running_correct / max(total_items, 1)
    return avg_loss, acc, np.asarray(all_labels), np.asarray(all_probs), np.asarray(all_preds)


def save_training_history(history):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history["train_loss"], label="Training loss", color="tab:blue")
    plt.plot(history["val_loss"], label="Validation loss", color="tab:orange")
    plt.title("Training vs Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(history["train_acc"], label="Training accuracy", color="tab:green")
    plt.plot(history["val_acc"], label="Validation accuracy", color="tab:red")
    plt.title("Training vs Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(TRAINING_CURVE_PATH, dpi=200)
    plt.close()


def compute_binary_metrics(true_labels, predicted_labels, probabilities):
    y_true = np.asarray(true_labels)
    y_pred = np.asarray(predicted_labels)
    y_prob = np.asarray(probabilities)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc_roc = roc_auc_score(y_true, y_prob[:, 1])

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "f1_score": float(f1),
        "auc_roc": float(auc_roc),
    }


def save_test_evaluation(test_metrics, confusion_matrix_values, prediction_rows):
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(METRICS_DIR / "test_metrics.json", "w", encoding="utf-8") as handle:
        json.dump(test_metrics, handle, indent=2)

    np.savetxt(METRICS_DIR / "confusion_matrix.csv", confusion_matrix_values, delimiter=",", fmt="%d")

    prediction_frame = pd.DataFrame(prediction_rows)
    prediction_frame.to_csv(METRICS_DIR / "test_predictions.csv", index=False)


def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    labels = ["Normal", "Pancreatic Tumour"]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(np.arange(2))
    ax.set_yticks(np.arange(2))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title("Confusion Matrix")

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=200)
    plt.close(fig)
    return cm


def plot_roc_curve(y_true, probabilities):
    from sklearn.metrics import roc_curve

    fpr, tpr, _ = roc_curve(y_true, probabilities[:, 1])
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc_score(y_true, probabilities[:, 1]):.3f})", color="tab:blue")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "roc_curve.png", dpi=200)
    plt.close()


def run_training():
    set_seed(RANDOM_SEED)
    print_system_info()

    print("Verifying dataset folders...")
    verify_dataset_structure()
    print("Detected image counts before training:")
    for folder in [
        PROJECT_ROOT / "dataset" / "train" / "normal",
        PROJECT_ROOT / "dataset" / "train" / "pancreatic_tumor",
        PROJECT_ROOT / "dataset" / "test" / "normal",
        PROJECT_ROOT / "dataset" / "test" / "pancreatic_tumor",
    ]:
        count = len([p for p in folder.rglob("*") if p.is_file()])
        print(f"  {folder}: {count}")

    train_paths, train_labels, val_paths, val_labels, test_paths, test_labels = prepare_dataset_splits()
    train_loader, val_loader, test_loader = build_dataloaders(
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
        batch_size=BATCH_SIZE,
    )

    class_weights = compute_class_weights(train_labels)
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    print("Class counts and weights:")
    for idx, class_name in enumerate(CLASS_NAMES):
        print(f"  {class_name}: count={sum(1 for label in train_labels if label == idx)}, weight={class_weights[idx].item():.4f}")

    device = get_device()
    model = build_resnet50_model(pretrained=True, freeze_backbone=FREEZE_BACKBONE, use_cbam=True)
    model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scaler = torch.cuda.amp.GradScaler(enabled=(USE_MIXED_PRECISION and device.type == "cuda")) if USE_MIXED_PRECISION and device.type == "cuda" else None

    best_val_loss = math.inf
    best_state = None
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    for epoch in range(1, EPOCHS + 1):
        start_time = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device, scaler)
        val_loss, val_acc, val_labels_numpy, val_probs, val_preds = evaluate_model(model, val_loader, criterion, device, scaler)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        epoch_duration = time.time() - start_time
        print(
            f"Epoch {epoch}/{EPOCHS} - "
            f"train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}, "
            f"lr={optimizer.param_groups[0]['lr']:.6f}, "
            f"time={epoch_duration:.1f}s"
        )

        if val_loss < best_val_loss - MIN_DELTA:
            best_val_loss = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"Early stopping triggered at epoch {epoch}.")
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    save_training_history(history)
    model_config = {
        "model_name": "ResNet50",
        "class_mapping": CLASS_TO_INDEX,
        "class_names": CLASS_NAMES,
        "input_size": 224,
        "normalization": get_preprocessing_config(),
    }

    checkpoint = {
        "model_state": model.state_dict(),
        "config": model_config,
        "history": history,
    }
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, MODEL_PATH)
    torch.save(checkpoint, MODEL_ALIAS_PATH)

    test_loss, test_acc, true_labels, test_probs, test_preds = evaluate_model(model, test_loader, criterion, device, scaler)
    test_metrics = compute_binary_metrics(true_labels, test_preds, test_probs)
    cm = plot_confusion_matrix(true_labels, test_preds)
    plot_roc_curve(true_labels, test_probs)

    prediction_rows = []
    for idx, file_path in enumerate(test_loader.dataset.file_paths):
        label_idx = int(test_labels[idx])
        pred_idx = int(test_preds[idx])
        normal_prob = float(test_probs[idx, 0])
        tumour_prob = float(test_probs[idx, 1])
        prediction_rows.append(
            {
                "image_name": Path(file_path).name,
                "true_label": CLASS_NAMES[label_idx],
                "predicted_label": CLASS_NAMES[pred_idx],
                "normal_probability": normal_prob,
                "tumour_probability": tumour_prob,
            }
        )

    save_test_evaluation(test_metrics, cm, prediction_rows)

    print("\nFinal test metrics:")
    for key, value in test_metrics.items():
        print(f"  {key}: {value:.4f}")


if __name__ == "__main__":
    run_training()
