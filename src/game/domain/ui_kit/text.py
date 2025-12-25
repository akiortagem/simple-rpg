"""Text UI element."""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Color
from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Text:
    content: str
    position: tuple[int, int] | None = None
    color: Color = (255, 255, 255)
    size: int = 32
    center: bool = False

    def measure(self, bounds: Size) -> Size:
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        position = self.position or (bounds.x, bounds.y)
        rect = Rect(position[0], position[1], bounds.width, self.size)
        return LayoutNode(self, rect)
