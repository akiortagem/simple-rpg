"""Foundational UI layout types.

Defines ``Size``, ``Rect``, ``LayoutNode``, and the ``UIElement`` protocol used
by all declarative UI widgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class Size:
    width: int
    height: int


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def inset(self, amount: int) -> Rect:
        return Rect(
            self.x + amount,
            self.y + amount,
            max(self.width - amount * 2, 0),
            max(self.height - amount * 2, 0),
        )


class UIElement(Protocol):
    """Base protocol for UI elements that can be laid out."""

    def measure(self, bounds: Size) -> Size:
        """Return the preferred size for the element within bounds."""

    def layout(self, bounds: Rect) -> "LayoutNode":
        """Return a layout node describing where the element should render."""


@dataclass(frozen=True)
class LayoutNode:
    element: UIElement
    rect: Rect
    children: tuple["LayoutNode", ...] = ()


UIElements = Iterable[UIElement]
