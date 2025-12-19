"""Scene abstractions and example implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from .contracts import Color, InputEvent, Renderer


class Scene(ABC):
    """Base class representing a game scene.

    Scenes orchestrate domain logic and describe what should be rendered without
    depending on a specific rendering framework.
    """

    background_color: Color = (0, 0, 0)
    _exit_requested: bool = False

    def request_exit(self) -> None:
        """Ask the game loop to end after the current frame."""

        self._exit_requested = True

    def should_exit(self) -> bool:
        """Return whether the scene asked to stop the loop."""

        return self._exit_requested

    def on_enter(self) -> None:
        """Hook called when the scene becomes active."""
        return None

    def on_exit(self) -> None:
        """Hook called when the scene is replaced."""
        return None

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        """Process user input and other incoming events."""
        return None

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Advance the scene state by ``delta_time`` seconds."""

    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        """Issue rendering commands through the provided renderer."""


class DemoScene(Scene):
    """A minimal demo scene used for scaffolding."""

    background_color: Color = (15, 15, 28)

    def __init__(self) -> None:
        self._elapsed = 0.0

    def update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    def render(self, renderer: Renderer) -> None:
        renderer.clear(self.background_color)
        pulse = (abs(((self._elapsed % 2.0) / 2.0) - 0.5) * 2)
        base_size = 50
        size_variation = int(base_size + 30 * pulse)
        width, height = renderer.size
        rect = (
            width // 2 - size_variation // 2,
            height // 2 - size_variation // 2,
            size_variation,
            size_variation,
        )
        renderer.draw_rect((200, 220, 255), rect)
