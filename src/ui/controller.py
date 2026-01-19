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
from .keypress_detector import KeypressDetector
from .menu import Menu
from .positioned import Positioned


class UIController:
    """Track UI focus state and translate input events to UI updates."""

    def __init__(self, focused_index: int = 0) -> None:
        self.focused_index = focused_index
        self._has_focus = focused_index != 0

    def handle_events(self, events: Sequence[InputEvent], root: UIElement) -> None:
        """Update focus/selection state based on input events."""
        menu = self._find_menu(root)
        detectors = tuple(self._find_keypress_detectors(root))
        if menu is not None:
            self._sync_focus(menu)
        for event in events:
            if event.type != "KEYDOWN" or not event.payload:
                continue
            key = event.payload.get("key")
            handled = False
            for detector in detectors:
                if detector.on_keypress and isinstance(key, str):
                    if detector.on_keypress(key):
                        handled = True
            if handled:
                event.payload["handled"] = True
                continue
            if key == Key.UP and menu is not None:
                self._has_focus = True
                self.focused_index -= 1
                self._clamp_focus(menu)
                event.payload["handled"] = True
            elif key == Key.DOWN and menu is not None:
                self._has_focus = True
                self.focused_index += 1
                self._clamp_focus(menu)
                event.payload["handled"] = True
            elif key == Key.ENTER:
                if menu is not None:
                    menu.select(self.focused_index).activate()
                for detector in detectors:
                    if detector.on_interact:
                        detector.on_interact()
                event.payload["handled"] = True

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
        if isinstance(element, Positioned) and element.content:
            return replace(element, content=self._apply_focus(element.content))
        if isinstance(element, KeypressDetector) and element.content:
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
        if isinstance(element, Positioned) and element.content:
            return self._find_menu(element.content)
        if isinstance(element, KeypressDetector) and element.content:
            return self._find_menu(element.content)
        if isinstance(element, Column):
            for child in element.contents:
                found = self._find_menu(child)
                if found:
                    return found
        return None

    def _find_keypress_detectors(self, element: UIElement) -> list[KeypressDetector]:
        detectors: list[KeypressDetector] = []
        if isinstance(element, KeypressDetector):
            detectors.append(element)
            if element.content:
                detectors.extend(self._find_keypress_detectors(element.content))
            return detectors
        if isinstance(element, Container) and element.content:
            detectors.extend(self._find_keypress_detectors(element.content))
        if isinstance(element, Center) and element.content:
            detectors.extend(self._find_keypress_detectors(element.content))
        if isinstance(element, Positioned) and element.content:
            detectors.extend(self._find_keypress_detectors(element.content))
        if isinstance(element, Column):
            for child in element.contents:
                detectors.extend(self._find_keypress_detectors(child))
        return detectors
