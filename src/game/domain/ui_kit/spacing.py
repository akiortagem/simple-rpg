"""Spacing UI element."""

from __future__ import annotations

from dataclasses import dataclass

from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Spacing:
    size: int

    def measure(self, bounds: Size) -> Size:
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        rect = Rect(bounds.x, bounds.y, bounds.width, self.size)
        return LayoutNode(self, rect)
