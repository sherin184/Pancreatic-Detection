from __future__ import annotations

import torch
from torch import nn
from torchvision import models

from .cbam import CBAMBlock

MODEL_NAME = "ResNet50"
INPUT_IMAGE_SIZE = 224
CLASS_MAPPING = {"Normal": 0, "Pancreatic Tumour": 1}


class ResNet50BinaryClassifier(nn.Module):
    """Transfer-learning ResNet50 classifier for binary normal-versus-tumour classification."""

    def __init__(self, num_classes: int = 2, pretrained: bool = True, freeze_backbone: bool = True, use_cbam: bool = False):
        super().__init__()
        weights = models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
        self.model = models.resnet50(weights=weights)
        self.use_cbam = use_cbam

        in_features = self.model.fc.in_features
        self.model.fc = nn.Identity()
        self.classifier = nn.Linear(in_features, num_classes)
        if self.use_cbam:
            self.cbam = CBAMBlock(in_channels=in_features)

        if freeze_backbone:
            for param in self.model.parameters():
                param.requires_grad = False
            for param in self.classifier.parameters():
                param.requires_grad = True
            if self.use_cbam:
                for param in self.cbam.parameters():
                    param.requires_grad = True

    def forward(self, x):
        features = self.model(x)
        if self.use_cbam:
            features = self.cbam(features.view(features.size(0), features.size(1), 1, 1)).flatten(1)
        return self.classifier(features)


class ResNet50CBAMBinaryClassifier(ResNet50BinaryClassifier):
    def __init__(self, num_classes: int = 2, pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__(num_classes=num_classes, pretrained=pretrained, freeze_backbone=freeze_backbone, use_cbam=True)


def build_resnet50_model(num_classes: int = 2, pretrained: bool = True, freeze_backbone: bool = True, use_cbam: bool = False):
    if use_cbam:
        return ResNet50CBAMBinaryClassifier(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_backbone=freeze_backbone,
        )
    return ResNet50BinaryClassifier(
        num_classes=num_classes,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
        use_cbam=False,
    )


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def print_system_info():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("GPU name:", torch.cuda.get_device_name(0))
    else:
        print("GPU name: CPU")
    device = get_device()
    print("Selected device:", device)
    return device
