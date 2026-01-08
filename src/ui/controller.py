"""UI controller for focus and input handling.

Use ``UIController`` to manage focus movement and selection in menu-driven UI
scenes.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from ..core.contracts import InputEvent, Key
from .base import UIElement
from .center import Center
from .column import Column
from .container import Container
from .menu import Menu


class UIController:
    """Track UI focus state and translate input events to UI updates."""

    def __init__(self, focused_index: int = 0) -> None:
        self.focused_index = focused_index
        self._has_focus = focused_index != 0

    def handle_events(self, events: Sequence[InputEvent], root: UIElement) -> None:
        """Update focus/selection state based on input events."""
        menu = self._find_menu(root)
        if menu is None:
            return
        self._sync_focus(menu)
        for event in events:
            if event.type != "KEYDOWN" or not event.payload:
                continue
            key = event.payload.get("key")
            if key == Key.UP:
                self._has_focus = True
                self.focused_index -= 1
                self._clamp_focus(menu)
            elif key == Key.DOWN:
                self._has_focus = True
                self.focused_index += 1
                self._clamp_focus(menu)
            elif key == Key.ENTER:
                menu.select(self.focused_index).activate()

    def apply(self, root: UIElement) -> UIElement:
        """Return a UI tree with focus applied to menu selections."""
        return self._apply_focus(root)

    def _sync_focus(self, menu: Menu) -> None:
        if not self._has_focus:
            self.focused_index = menu.selected_index
        self._clamp_focus(menu)

    def _clamp_focus(self, menu: Menu) -> None:
        max_index = max(len(menu.choices) - 1, 0)
        self.focused_index = max(0, min(self.focused_index, max_index))

    def _apply_focus(self, element: UIElement) -> UIElement:
        if isinstance(element, Menu):
            self._sync_focus(element)
            return element.select(self.focused_index)
        if isinstance(element, Container) and element.content:
            return replace(element, content=self._apply_focus(element.content))
        if isinstance(element, Center) and element.content:
            return replace(element, content=self._apply_focus(element.content))
        if isinstance(element, Column):
            return replace(
                element,
                contents=tuple(self._apply_focus(child) for child in element.contents),
            )
        return element

    def _find_menu(self, element: UIElement) -> Menu | None:
        if isinstance(element, Menu):
            return element
        if isinstance(element, Container) and element.content:
            return self._find_menu(element.content)
        if isinstance(element, Center) and element.content:
            return self._find_menu(element.content)
        if isinstance(element, Column):
            for child in element.contents:
                found = self._find_menu(child)
                if found:
                    return found
        return None
