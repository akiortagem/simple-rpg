"""Spacing UI element.

Use ``Spacing`` to insert fixed gaps between other UI components.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Spacing:
    """Fixed vertical spacer in layout trees."""

    size: int

    def measure(self, bounds: Size) -> Size:
        """Return the size with the fixed height."""
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node with the fixed height."""
        rect = Rect(bounds.x, bounds.y, bounds.width, self.size)
        return LayoutNode(self, rect)
