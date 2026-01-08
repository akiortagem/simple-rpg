"""Positioned UI element.

Use ``Positioned`` to anchor or stretch a child within bounds using offsets.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import LayoutNode, Rect, Size, UIElement


@dataclass(frozen=True)
class Positioned:
    """Positions a child with optional offsets on each side."""

    top: int | None = None
    bottom: int | None = None
    left: int | None = None
    right: int | None = None
    content: UIElement | None = None

    def measure(self, bounds: Size) -> Size:
        """Return the preferred size within bounds based on offsets."""
        content_size = self.content.measure(bounds) if self.content else Size(0, 0)

        if self.left is not None and self.right is not None:
            width = max(bounds.width - self.left - self.right, 0)
        else:
            width = min(content_size.width, bounds.width)

        if self.top is not None and self.bottom is not None:
            height = max(bounds.height - self.top - self.bottom, 0)
        else:
            height = min(content_size.height, bounds.height)

        return Size(width, height)

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node for the positioned child."""
        children: list[LayoutNode] = []
        if not self.content:
            return LayoutNode(self, bounds, tuple(children))

        content_size = self.content.measure(bounds.size)

        if self.left is not None and self.right is not None:
            width = max(bounds.width - self.left - self.right, 0)
        else:
            width = min(content_size.width, bounds.width)

        if self.top is not None and self.bottom is not None:
            height = max(bounds.height - self.top - self.bottom, 0)
        else:
            height = min(content_size.height, bounds.height)

        width = max(min(width, bounds.width), 0)
        height = max(min(height, bounds.height), 0)

        if self.left is not None:
            x = bounds.x + self.left
        elif self.right is not None:
            x = bounds.x + bounds.width - self.right - width
        else:
            x = bounds.x

        if self.top is not None:
            y = bounds.y + self.top
        elif self.bottom is not None:
            y = bounds.y + bounds.height - self.bottom - height
        else:
            y = bounds.y

        x = min(max(x, bounds.x), bounds.x + bounds.width - width)
        y = min(max(y, bounds.y), bounds.y + bounds.height - height)

        rect = Rect(x, y, width, height)
        children.append(self.content.layout(rect))
        return LayoutNode(self, bounds, tuple(children))
