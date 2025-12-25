"""Container UI element."""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Color
from .base import LayoutNode, Rect, Size, UIElement
from .border import Border


@dataclass(frozen=True)
class Container:
    background_color: Color = (0, 0, 0)
    border: Border | None = None
    content: UIElement | None = None

    def measure(self, bounds: Size) -> Size:
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        children: list[LayoutNode] = []
        if self.border:
            children.append(self.border.layout(bounds))
            inner_bounds = bounds.inset(self.border.width)
        else:
            inner_bounds = bounds
        if self.content:
            children.append(self.content.layout(inner_bounds))
        return LayoutNode(self, bounds, tuple(children))
