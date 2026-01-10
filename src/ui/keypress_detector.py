"""Keypress detector UI element.

Use ``KeypressDetector`` to attach an interaction callback to a UI subtree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .base import LayoutNode, Rect, Size, UIElement


@dataclass(frozen=True)
class KeypressDetector:
    """Wraps a child element and listens for interaction keypresses."""

    content: UIElement | None = None
    on_interact: Callable[[], None] | None = None

    def measure(self, bounds: Size) -> Size:
        """Return the preferred size of the content element."""
        if not self.content:
            return Size(0, 0)
        return self.content.measure(bounds)

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node that forwards to the child."""
        children: list[LayoutNode] = []
        if self.content:
            children.append(self.content.layout(bounds))
        return LayoutNode(self, bounds, tuple(children))
