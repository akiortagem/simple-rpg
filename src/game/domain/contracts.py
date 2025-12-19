"""Domain-level contracts to decouple game logic from frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple

Color = Tuple[int, int, int]


@dataclass
class InputEvent:
    """A framework-agnostic input event."""

    type: str
    payload: dict[str, object] | None = None


class Key:
    """Named key constants for framework-agnostic input handling."""

    UP = "UP"
    DOWN = "DOWN"
    ENTER = "ENTER"


class Renderer(Protocol):
    """Abstraction for drawing to the screen."""

    @property
    def size(self) -> tuple[int, int]:
        """Return the width and height of the renderable surface."""
        raise NotImplementedError

    def clear(self, color: Color) -> None:
        """Clear the surface with a solid color."""
        raise NotImplementedError

    def draw_rect(self, color: Color, rect: tuple[int, int, int, int]) -> None:
        """Draw a filled rectangle."""
        raise NotImplementedError

    def draw_image(
        self,
        image: object,
        source_rect: tuple[int, int, int, int],
        destination: tuple[int, int],
    ) -> None:
        """Blit a subsection of an image at the destination point."""
        raise NotImplementedError

    def draw_text(
        self,
        text: str,
        position: tuple[int, int],
        color: Color,
        font_size: int = 32,
        center: bool = False,
    ) -> None:
        """Draw text anchored at the given position."""
        raise NotImplementedError

    def present(self) -> None:
        """Flush any pending drawing to the screen."""
        raise NotImplementedError


class EventSource(Protocol):
    """Supplies framework-agnostic input events."""

    def poll(self) -> Sequence[InputEvent]:
        raise NotImplementedError


class TimeSource(Protocol):
    """Provides frame timing information."""

    def tick(self, target_fps: int) -> float:
        """Return the delta time (in seconds) since the last tick."""
        raise NotImplementedError
