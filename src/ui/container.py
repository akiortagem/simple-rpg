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
    width: int | None = None
    height: int | None = None

    def measure(self, bounds: Size) -> Size:
        """Return the preferred size for the container within bounds."""
        content_size = self.content.measure(bounds) if self.content else bounds
        width = self.width if self.width is not None else content_size.width
        height = self.height if self.height is not None else content_size.height
        return Size(min(width, bounds.width), min(height, bounds.height))

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout tree including border and content."""
        measured_size = self.measure(bounds.size)
        layout_bounds = Rect(
            bounds.x,
            bounds.y,
            measured_size.width,
            measured_size.height,
        )
        children: list[LayoutNode] = []
        if self.border:
            children.append(self.border.layout(layout_bounds))
            inner_bounds = layout_bounds.inset(self.border.width)
        else:
            inner_bounds = layout_bounds
        if self.content:
            children.append(self.content.layout(inner_bounds))
        return LayoutNode(self, layout_bounds, tuple(children))
