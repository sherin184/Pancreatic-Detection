from __future__ import annotations

from torchvision import transforms

IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_train_transform(input_size: int = IMAGE_SIZE):
    """Training augmentation for medical image classification with mild transformations."""
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(input_size, scale=(0.85, 1.0), ratio=(0.95, 1.05)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.10, contrast=0.10, saturation=0.05, hue=0.02),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def build_eval_transform(input_size: int = IMAGE_SIZE):
    """Deterministic validation or test transform without augmentation."""
    return transforms.Compose(
        [
            transforms.Resize(int(input_size * 1.1)),
            transforms.CenterCrop(input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_preprocessing_config():
    return {
        "input_size": IMAGE_SIZE,
        "mean": IMAGENET_MEAN,
        "std": IMAGENET_STD,
    }
