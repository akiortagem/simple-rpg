"""Text UI element.

Use ``Text`` for rendering labels and informational strings inside layouts.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.contracts import Color
from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class Text:
    """Text label element with configurable font size and color."""

    content: str
    position: tuple[int, int] | None = None
    color: Color = (255, 255, 255)
    size: int = 32
    center: bool = False

    def measure(self, bounds: Size) -> Size:
        """Return the size used for the text row."""
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node for the text element."""
        position = self.position or (bounds.x, bounds.y)
        rect = Rect(position[0], position[1], bounds.width, self.size)
        return LayoutNode(self, rect)
