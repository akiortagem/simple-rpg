"""Pygame infrastructure adapters implementing domain contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pygame

from ..domain.contracts import Color, EventSource, InputEvent, Key, Renderer, TimeSource
from .assets import load_image


class PygameRenderer(Renderer):
    """Render commands backed by a pygame display surface."""

    def __init__(self, size: tuple[int, int], title: str) -> None:
        self._surface = pygame.display.set_mode(size)
        pygame.display.set_caption(title)
        self._image_cache: dict[Path, pygame.Surface] = {}

    @property
    def size(self) -> tuple[int, int]:
        return self._surface.get_size()

    def clear(self, color: Color) -> None:
        self._surface.fill(color)

    def draw_rect(self, color: Color, rect: tuple[int, int, int, int]) -> None:
        pygame.draw.rect(self._surface, color, rect)

    def draw_rect_outline(
        self,
        color: Color,
        rect: tuple[int, int, int, int],
        width: int = 1,
    ) -> None:
        pygame.draw.rect(self._surface, color, rect, width=width)

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
        image: object,
        source_rect: tuple[int, int, int, int],
        destination: tuple[int, int],
    ) -> None:
        """Draw a subsection of an image onto the main surface."""

        resolved = self._resolve_image(image, source_rect)
        self._surface.blit(resolved, destination, source_rect)

    def present(self) -> None:
        pygame.display.flip()

    def _resolve_image(
        self,
        image: object,
        source_rect: tuple[int, int, int, int],
    ) -> pygame.Surface:
        if isinstance(image, (str, Path)):
            path = Path(image)
            width = max(source_rect[0] + source_rect[2], source_rect[2], 1)
            height = max(source_rect[1] + source_rect[3], source_rect[3], 1)
            cached = self._image_cache.get(path)
            if cached and cached.get_width() >= width and cached.get_height() >= height:
                return cached
            loaded = load_image(path, (width, height), (200, 0, 200))
            self._image_cache[path] = loaded
            return loaded
        if not isinstance(image, pygame.Surface):
            raise TypeError("Renderer expected a file path or pygame.Surface image.")
        return image


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
