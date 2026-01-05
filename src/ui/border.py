"""Border UI element.

Use ``Border`` to wrap other UI content and draw a rectangular outline.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.contracts import Color
from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Border:
    """Draws a rectangular outline around layout bounds."""

    color: Color = (255, 255, 255)
    width: int = 2

    def measure(self, bounds: Size) -> Size:
        """Return the bounds unchanged."""
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node for the border."""
        return LayoutNode(self, bounds)
