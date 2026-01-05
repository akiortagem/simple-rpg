"""Column layout UI element.

Use ``Column`` to stack UI children vertically with spacing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .base import LayoutNode, Rect, Size, UIElement


@dataclass(frozen=True)
class Column:
    """Vertically stacks child UI elements with optional spacing."""

    contents: Sequence[UIElement]
    spacing: int = 0

    def measure(self, bounds: Size) -> Size:
        """Return the layout size for the column within the given bounds."""
        total_height = 0
        for idx, child in enumerate(self.contents):
            if idx:
                total_height += self.spacing
            total_height += child.measure(bounds).height
        return Size(bounds.width, min(bounds.height, total_height))

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout tree for the column and its children."""
        children: list[LayoutNode] = []
        cursor_y = bounds.y
        for idx, child in enumerate(self.contents):
            if idx:
                cursor_y += self.spacing
            child_size = child.measure(bounds.size)
            child_rect = Rect(bounds.x, cursor_y, bounds.width, child_size.height)
            children.append(child.layout(child_rect))
            cursor_y += child_size.height
        return LayoutNode(self, bounds, tuple(children))
