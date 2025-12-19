"""Pygame infrastructure adapters implementing domain contracts."""

from __future__ import annotations

from typing import Sequence

import pygame

from ..domain.contracts import Color, EventSource, InputEvent, Key, Renderer, TimeSource


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

    def draw_text(
        self,
        text: str,
        position: tuple[int, int],
        color: Color,
        font_size: int = 32,
        center: bool = False,
    ) -> None:
        font = pygame.font.SysFont(None, font_size)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        self._surface.blit(rendered, rect)

    def draw_image(
        self,
        image: pygame.Surface,
        source_rect: tuple[int, int, int, int],
        destination: tuple[int, int],
    ) -> None:
        """Draw a subsection of an image onto the main surface."""

        self._surface.blit(image, destination, source_rect)

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
                converted.append(InputEvent(type="KEYDOWN", payload={"key": self._translate_key(event.key)}))
            elif event.type == pygame.KEYUP:
                converted.append(InputEvent(type="KEYUP", payload={"key": self._translate_key(event.key)}))
        return converted

    @staticmethod
    def _translate_key(raw_key: int) -> str | int:
        """Map pygame key constants to framework key names when possible."""

        mapping = {
            pygame.K_UP: Key.UP,
            pygame.K_DOWN: Key.DOWN,
            pygame.K_LEFT: Key.LEFT,
            pygame.K_RIGHT: Key.RIGHT,
            pygame.K_RETURN: Key.ENTER,
            pygame.K_KP_ENTER: Key.ENTER,
        }
        return mapping.get(raw_key, raw_key)


class PygameClock(TimeSource):
    """Provide delta time using pygame's Clock."""

    def __init__(self) -> None:
        self._clock = pygame.time.Clock()

    def tick(self, target_fps: int) -> float:
        milliseconds = self._clock.tick(target_fps)
        return milliseconds / 1000.0
