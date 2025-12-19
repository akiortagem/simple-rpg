"""Pygame infrastructure adapters implementing domain contracts."""

from __future__ import annotations

from typing import Sequence

import pygame

from ..domain.contracts import Color, EventSource, InputEvent, Renderer, TimeSource


class PygameRenderer(Renderer):
    """Render commands backed by a pygame display surface."""

    def __init__(self, size: tuple[int, int], title: str) -> None:
        self._surface = pygame.display.set_mode(size)
        pygame.display.set_caption(title)

    @property
    def size(self) -> tuple[int, int]:
        return self._surface.get_size()

    def clear(self, color: Color) -> None:
        self._surface.fill(color)

    def draw_rect(self, color: Color, rect: tuple[int, int, int, int]) -> None:
        pygame.draw.rect(self._surface, color, rect)

    def present(self) -> None:
        pygame.display.flip()


class PygameEventSource(EventSource):
    """Translate pygame events into framework-agnostic input events."""

    def poll(self) -> Sequence[InputEvent]:
        converted: list[InputEvent] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                converted.append(InputEvent(type="QUIT"))
            elif event.type == pygame.KEYDOWN:
                converted.append(
                    InputEvent(type="KEYDOWN", payload={"key": event.key})
                )
            elif event.type == pygame.KEYUP:
                converted.append(InputEvent(type="KEYUP", payload={"key": event.key}))
        return converted


class PygameClock(TimeSource):
    """Provide delta time using pygame's Clock."""

    def __init__(self) -> None:
        self._clock = pygame.time.Clock()

    def tick(self, target_fps: int) -> float:
        milliseconds = self._clock.tick(target_fps)
        return milliseconds / 1000.0
