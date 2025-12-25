"""Menu UI element."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Sequence

from .base import LayoutNode, Rect, Size
from .column import Column
from .menu_choice import MenuChoice


@dataclass(frozen=True)
class Menu:
    choices: Sequence[MenuChoice]
    spacing: int = 4
    selected_index: int = 0
    on_choose: Callable[[str | None], None] | None = None

    def select(self, index: int) -> "Menu":
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
        if not choice:
            return
        if choice.on_select:
            choice.on_select(choice)
        if self.on_choose:
            self.on_choose(choice.value)

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
