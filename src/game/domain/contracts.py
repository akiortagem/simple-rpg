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
