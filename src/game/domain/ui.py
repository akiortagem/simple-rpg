"""Declarative, immutable UI components and layout helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable, Protocol, Sequence

from .contracts import Color


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


@dataclass(frozen=True)
class LayoutNode:
    element: UIElement
    rect: Rect
    children: tuple[LayoutNode, ...] = ()


class UIElement(Protocol):
    """Base protocol for UI elements that can be laid out."""

    def measure(self, bounds: Size) -> Size:
        """Return the preferred size for the element within bounds."""

    def layout(self, bounds: Rect) -> LayoutNode:
        """Return a layout node describing where the element should render."""


@dataclass(frozen=True)
class Text:
    content: str
    position: tuple[int, int] | None = None
    color: Color = (255, 255, 255)
    size: int = 32
    center: bool = False

    def measure(self, bounds: Size) -> Size:
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        position = self.position or (bounds.x, bounds.y)
        rect = Rect(position[0], position[1], bounds.width, self.size)
        return LayoutNode(self, rect)


@dataclass(frozen=True)
class Border:
    color: Color = (255, 255, 255)
    width: int = 2

    def measure(self, bounds: Size) -> Size:
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        return LayoutNode(self, bounds)


@dataclass(frozen=True)
class Container:
    background_color: Color = (0, 0, 0)
    border: Border | None = None
    content: UIElement | None = None

    def measure(self, bounds: Size) -> Size:
        return bounds

    def layout(self, bounds: Rect) -> LayoutNode:
        children: list[LayoutNode] = []
        if self.border:
            children.append(self.border.layout(bounds))
            inner_bounds = bounds.inset(self.border.width)
        else:
            inner_bounds = bounds
        if self.content:
            children.append(self.content.layout(inner_bounds))
        return LayoutNode(self, bounds, tuple(children))


@dataclass(frozen=True)
class Spacing:
    size: int

    def measure(self, bounds: Size) -> Size:
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        rect = Rect(bounds.x, bounds.y, bounds.width, self.size)
        return LayoutNode(self, rect)


@dataclass(frozen=True)
class Column:
    contents: Sequence[UIElement]
    spacing: int = 0

    def measure(self, bounds: Size) -> Size:
        total_height = 0
        for idx, child in enumerate(self.contents):
            if idx:
                total_height += self.spacing
            total_height += child.measure(bounds).height
        return Size(bounds.width, min(bounds.height, total_height))

    def layout(self, bounds: Rect) -> LayoutNode:
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


@dataclass(frozen=True)
class MenuChoice:
    label: str
    selected: bool = False
    value: str | None = None
    on_select: Callable[[MenuChoice], None] | None = None
    color: Color = (255, 255, 255)
    selected_color: Color = (255, 220, 120)
    size: int = 32
    center: bool = False
    position: tuple[int, int] | None = None

    @property
    def display_color(self) -> Color:
        return self.selected_color if self.selected else self.color

    @property
    def display_label(self) -> str:
        prefix = "> " if self.selected else "  "
        return f"{prefix}{self.label}"

    def measure(self, bounds: Size) -> Size:
        return Size(bounds.width, self.size)

    def layout(self, bounds: Rect) -> LayoutNode:
        position = self.position or (bounds.x, bounds.y)
        rect = Rect(position[0], position[1], bounds.width, self.size)
        return LayoutNode(self, rect)


@dataclass(frozen=True)
class Menu:
    choices: Sequence[MenuChoice]
    spacing: int = 4
    selected_index: int = 0

    def select(self, index: int) -> Menu:
        clamped = max(0, min(index, len(self.choices) - 1))
        return replace(self, selected_index=clamped)

    @property
    def selected_choice(self) -> MenuChoice | None:
        if not self.choices:
            return None
        if self.selected_index < 0 or self.selected_index >= len(self.choices):
            return None
        return self.choices[self.selected_index]

    def activate(self) -> None:
        choice = self.selected_choice
        if choice and choice.on_select:
            choice.on_select(choice)

    def _resolved_choices(self) -> tuple[MenuChoice, ...]:
        resolved: list[MenuChoice] = []
        for idx, choice in enumerate(self.choices):
            if idx == self.selected_index and not choice.selected:
                resolved.append(replace(choice, selected=True))
            elif idx != self.selected_index and choice.selected:
                resolved.append(replace(choice, selected=False))
            else:
                resolved.append(choice)
        return tuple(resolved)

    def measure(self, bounds: Size) -> Size:
        column = Column(self._resolved_choices(), spacing=self.spacing)
        return column.measure(bounds)

    def layout(self, bounds: Rect) -> LayoutNode:
        column = Column(self._resolved_choices(), spacing=self.spacing)
        column_node = column.layout(bounds)
        return LayoutNode(self, bounds, column_node.children)


UIElements = Iterable[UIElement]
