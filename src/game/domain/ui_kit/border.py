"""Border UI element."""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Color
from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Border:
    color: Color = (255, 255, 255)
    width: int = 2

    def measure(self, bounds: Size) -> Size:
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        return LayoutNode(self, bounds)
