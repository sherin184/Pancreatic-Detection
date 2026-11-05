from __future__ import annotations

import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

from .preprocessing import build_eval_transform, build_train_transform

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "dataset"
RANDOM_SEED = 42
BATCH_SIZE = 16

NORMAL_CLASS = "Normal"
TUMOUR_CLASS = "Pancreatic Tumour"
CLASS_NAMES = [NORMAL_CLASS, TUMOUR_CLASS]
CLASS_TO_INDEX = {
    "normal": 0,
    NORMAL_CLASS: 0,
    "pancreatic_tumor": 1,
    "pancreatic_tumour": 1,
    "pancreatic tumor": 1,
    "pancreatic tumour": 1,
    TUMOUR_CLASS: 1,
}
CLASS_ALIASES = {
    "normal": NORMAL_CLASS,
    "pancreatic_tumor": TUMOUR_CLASS,
    "pancreatic_tumour": TUMOUR_CLASS,
    "pancreatic tumor": TUMOUR_CLASS,
    "pancreatic tumour": TUMOUR_CLASS,
    "pancreatic cancer": TUMOUR_CLASS,
    "Pancreatic Cancer": TUMOUR_CLASS,
    "Pancreatic Tumour": TUMOUR_CLASS,
    "Pancreatic Tumor": TUMOUR_CLASS,
    "Normal": NORMAL_CLASS,
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def _normalize_class_token(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


class PancreaticImageDataset(Dataset):
    """Dataset that stores file paths and labels for image classification."""

    def __init__(self, file_paths: List[Path], labels: List[int], transform=None):
        self.file_paths = list(file_paths)
        self.labels = list(labels)
        self.transform = transform

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        image_path = self.file_paths[idx]
        label = self.labels[idx]

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as exc:  # pragma: no cover - dataset validation handles errors early.
            raise RuntimeError(f"Unable to open image: {image_path}") from exc

        if self.transform is not None:
            image = self.transform(image)

        return image, label, str(image_path)


def _list_image_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted(
        path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def _resolve_class_folder(root: Path, class_name: str) -> Path | None:
    if not root.exists():
        return None

    target_label = _normalize_class_token(class_name)

    for candidate in sorted(root.iterdir()):
        if not candidate.is_dir():
            continue
        normalized = _normalize_class_token(candidate.name)
        if normalized == target_label:
            return candidate
        if normalized in CLASS_ALIASES and CLASS_ALIASES[normalized] == class_name:
            return candidate
        if normalized in CLASS_TO_INDEX and CLASS_TO_INDEX[normalized] == CLASS_TO_INDEX.get(target_label):
            return candidate
    return None


def _class_files_for_root(root: Path, class_name: str) -> List[Path]:
    class_dir = _resolve_class_folder(root, class_name)
    if class_dir is None:
        return []
    return _list_image_files(class_dir)


def verify_dataset_structure(dataset_root: Path = DATASET_ROOT):
    """Check that the expected train and test directories are present."""
    training_root = dataset_root / "train"
    testing_root = dataset_root / "test"

    if not training_root.exists():
        raise FileNotFoundError(f"Training folder not found: {training_root}. Expected dataset/train.")
    if not testing_root.exists():
        raise FileNotFoundError(f"Testing folder not found: {testing_root}. Expected dataset/test.")

    missing_dirs = []
    for class_name in CLASS_NAMES:
        if not _resolve_class_folder(training_root, class_name):
            missing_dirs.append(f"train/{_normalize_class_token(class_name)}")
        if not _resolve_class_folder(testing_root, class_name):
            missing_dirs.append(f"test/{_normalize_class_token(class_name)}")

    if missing_dirs:
        raise FileNotFoundError(
            "Dataset folders not found for the required labels: " + ", ".join(missing_dirs)
        )

    for stage_name, stage_root in [("train", training_root), ("test", testing_root)]:
        for class_name in CLASS_NAMES:
            folder = _resolve_class_folder(stage_root, class_name)
            if folder is not None:
                count = len(_list_image_files(folder))
                print(f"{stage_root / folder.name}: {count}")

    return training_root, testing_root


def count_images_per_class(root: Path, label_name: str) -> int:
    return len(_class_files_for_root(root, label_name))


def inspect_dataset(dataset_root: Path = DATASET_ROOT):
    """Inspect dataset contents and return summary statistics for notebook analysis."""
    verify_dataset_structure(dataset_root)

    summary = {
        "training": {},
        "testing": {},
        "image_dimensions": [],
        "formats": Counter(),
        "corrupted_images": [],
        "min_size": None,
        "max_size": None,
        "average_dimensions": None,
    }

    for stage_name, folder_name in [("Training", "train"), ("Testing", "test")]:
        stage_root = dataset_root / folder_name
        class_summary = {label: 0 for label in CLASS_NAMES}
        for label in CLASS_NAMES:
            file_paths = _class_files_for_root(stage_root, label)
            class_summary[label] = len(file_paths)
            for file_path in file_paths:
                try:
                    with Image.open(file_path) as image:
                        width, height = image.size
                        summary["image_dimensions"].append((width, height))
                        summary["formats"][file_path.suffix.lower()] += 1
                        if summary["min_size"] is None or width * height < summary["min_size"]:
                            summary["min_size"] = width * height
                        if summary["max_size"] is None or width * height > summary["max_size"]:
                            summary["max_size"] = width * height
                except Exception:
                    summary["corrupted_images"].append(str(file_path))
        summary[stage_name.lower()] = class_summary

    if summary["image_dimensions"]:
        widths = np.array([dim[0] for dim in summary["image_dimensions"]], dtype=float)
        heights = np.array([dim[1] for dim in summary["image_dimensions"]], dtype=float)
        summary["average_dimensions"] = {
            "width": float(widths.mean()),
            "height": float(heights.mean()),
        }

    return summary


def prepare_dataset_splits(dataset_root: Path = DATASET_ROOT):
    """Split the Training folder into 80/20 stratified training and validation sets."""
    training_root, testing_root = verify_dataset_structure(dataset_root)

    train_paths: List[Path] = []
    train_labels: List[int] = []

    for class_name in CLASS_NAMES:
        paths = _class_files_for_root(training_root, class_name)
        if not paths:
            raise FileNotFoundError(f"No images were found for class: {class_name}")
        for file_path in paths:
            train_paths.append(file_path)
            train_labels.append(CLASS_TO_INDEX[class_name])

    if len(np.unique(train_labels)) < 2:
        raise ValueError("Each class must have at least one training image to perform a stratified split.")

    X_train, X_val, y_train, y_val = train_test_split(
        train_paths,
        train_labels,
        test_size=0.2,
        stratify=train_labels,
        random_state=RANDOM_SEED,
    )

    test_paths: List[Path] = []
    test_labels: List[int] = []

    for class_name in CLASS_NAMES:
        paths = _class_files_for_root(testing_root, class_name)
        if not paths:
            raise FileNotFoundError(f"No images were found for class in testing set: {class_name}")
        for file_path in paths:
            test_paths.append(file_path)
            test_labels.append(CLASS_TO_INDEX[class_name])

    return X_train, np.asarray(y_train, dtype=int), X_val, np.asarray(y_val, dtype=int), test_paths, np.asarray(test_labels, dtype=int)


def compute_class_weights(train_labels: List[int] | np.ndarray) -> np.ndarray:
    """Compute class weights for class-imbalanced training."""
    counts = np.bincount(np.asarray(train_labels, dtype=int), minlength=len(CLASS_NAMES))
    if np.any(counts == 0):
        raise ValueError(f"Class counts cannot be zero when computing weights: {counts}")

    class_weights = counts.sum() / (len(CLASS_NAMES) * counts)
    return class_weights.astype(np.float32)


def build_dataloaders(
    train_paths: List[Path],
    train_labels: List[int] | np.ndarray,
    val_paths: List[Path],
    val_labels: List[int] | np.ndarray,
    test_paths: List[Path],
    test_labels: List[int] | np.ndarray,
    batch_size: int = BATCH_SIZE,
):
    """Create training, validation, and test DataLoader objects using Windows-safe workers."""
    num_workers = 0 if os.name == "nt" else 2

    train_dataset = PancreaticImageDataset(list(train_paths), list(train_labels), transform=build_train_transform())
    val_dataset = PancreaticImageDataset(list(val_paths), list(val_labels), transform=build_eval_transform())
    test_dataset = PancreaticImageDataset(list(test_paths), list(test_labels), transform=build_eval_transform())

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    return train_loader, val_loader, test_loader


def print_dataset_summary(dataset_root: Path = DATASET_ROOT):
    """Convenience function for notebook and CLI reporting."""
    summary = inspect_dataset(dataset_root)
    print("Training class distribution:")
    for key, value in summary["training"].items():
        print(f"  {key}: {value}")
    print("\nTesting class distribution:")
    for key, value in summary["testing"].items():
        print(f"  {key}: {value}")
    print(f"\nImage formats: {dict(summary['formats'])}")
    print(f"Corrupted images: {summary['corrupted_images']}")
    if summary["average_dimensions"] is not None:
        print(
            "Average image dimensions: "
            f"{summary['average_dimensions']['width']:.1f} x {summary['average_dimensions']['height']:.1f}"
        )
    print(f"Min pixel area: {summary['min_size']}")
    print(f"Max pixel area: {summary['max_size']}")
    return summary
