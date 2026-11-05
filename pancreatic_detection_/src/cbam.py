from __future__ import annotations

import torch
from torch import nn


class ChannelAttention(nn.Module):
    """Channel-wise attention gate for feature recalibration."""

    def __init__(self, in_channels: int, reduction: int = 16):
        super().__init__()
        reduced_channels = max(1, in_channels // reduction)
        self.pool_avg = nn.AdaptiveAvgPool2d(1)
        self.pool_max = nn.AdaptiveMaxPool2d(1)
        self.fc1 = nn.Linear(in_channels, reduced_channels)
        self.fc2 = nn.Linear(reduced_channels, in_channels)
        self.activation = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg = self.pool_avg(x).flatten(1)
        max_ = self.pool_max(x).flatten(1)
        avg = self.fc2(self.activation(self.fc1(avg)))
        max_ = self.fc2(self.activation(self.fc1(max_)))
        attention = self.sigmoid(avg + max_).unsqueeze(-1).unsqueeze(-1)
        return x * attention


class SpatialAttention(nn.Module):
    """Spatial attention that highlights informative spatial regions."""

    def __init__(self, kernel_size: int = 7):
        super().__init__()
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg = x.mean(dim=1, keepdim=True)
        max_ = x.amax(dim=1, keepdim=True)
        combined = torch.cat([avg, max_], dim=1)
        attention = self.conv(combined)
        return x * self.sigmoid(attention)


class CBAMBlock(nn.Module):
    """Convolutional Block Attention Module (CBAM)."""

    def __init__(self, in_channels: int, reduction: int = 16, kernel_size: int = 7):
        super().__init__()
        self.channel_attention = ChannelAttention(in_channels=in_channels, reduction=reduction)
        self.spatial_attention = SpatialAttention(kernel_size=kernel_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.channel_attention(x)
        x = self.spatial_attention(x)
        return x
