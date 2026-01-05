"""Menu choice UI element.

Use ``MenuChoice`` to represent individual selectable items in a ``Menu``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..core.contracts import Color
from .base import LayoutNode, Rect, Size


@dataclass(frozen=True)
class MenuChoice:
    """Single selectable menu entry with display styling."""

    label: str
    selected: bool = False
    value: str | None = None
    on_select: Callable[["MenuChoice"], None] | None = None
    color: Color = (255, 255, 255)
    selected_color: Color = (255, 220, 120)
    highlight_color: Color | None = (40, 40, 80)
    highlight_padding: int = 6
    size: int = 32
    center: bool = False
    position: tuple[int, int] | None = None

    @property
    def display_color(self) -> Color:
        """Return the color based on selection state."""
        return self.selected_color if self.selected else self.color

    @property
    def display_label(self) -> str:
        """Return the rendered label with selection prefix."""
        prefix = "> " if self.selected else "  "
        return f"{prefix}{self.label}"

    def measure(self, bounds: Size) -> Size:
        """Return the size used for the choice row."""
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node for the choice label."""
        position = self.position or (bounds.x, bounds.y)
        rect = Rect(position[0], position[1], bounds.width, self.size)
        return LayoutNode(self, rect)
