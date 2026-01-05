"""Container UI element.

Use ``Container`` to apply padding and background colors around child elements.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.contracts import Color
from .base import LayoutNode, Rect, Size, UIElement
from .border import Border


@dataclass(frozen=True)
class Container:
    """Wraps a child element with background color and optional border."""

    background_color: Color = (0, 0, 0)
    border: Border | None = None
    content: UIElement | None = None

    def measure(self, bounds: Size) -> Size:
        """Return the bounds unchanged for container sizing."""
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout tree including border and content."""
        children: list[LayoutNode] = []
        if self.border:
            children.append(self.border.layout(bounds))
            inner_bounds = bounds.inset(self.border.width)
        else:
            inner_bounds = bounds
        if self.content:
            children.append(self.content.layout(inner_bounds))
        return LayoutNode(self, bounds, tuple(children))
