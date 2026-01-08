"""Centered layout UI element.

Use ``Center`` to position a single child in the middle of available bounds.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import LayoutNode, Rect, Size, UIElement


@dataclass(frozen=True)
class Center:
    """Centers a child UI element within available bounds."""

    content: UIElement | None = None

    def measure(self, bounds: Size) -> Size:
        """Return the bounds unchanged for center sizing."""
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout tree for the centered child."""
        children: list[LayoutNode] = []
        if self.content:
            child_size = self.content.measure(bounds.size)
            clamped_size = Size(
                min(child_size.width, bounds.width),
                min(child_size.height, bounds.height),
            )
            child_rect = Rect(
                bounds.x + (bounds.width - clamped_size.width) // 2,
                bounds.y + (bounds.height - clamped_size.height) // 2,
                clamped_size.width,
                clamped_size.height,
            )
            children.append(self.content.layout(child_rect))
        return LayoutNode(self, bounds, tuple(children))
