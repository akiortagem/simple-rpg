"""Scene abstractions and example implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Sequence

from .contracts import Color, InputEvent, Renderer
from .sprites import CharacterMapSprite, CollisionDetector


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


class RenderableTilemapLayer(Protocol):
    """Renderable background or foreground tile layer."""

    pixel_size: tuple[int, int] | None

    def render(self, renderer: Renderer, camera_offset: tuple[int, int] = (0, 0)) -> None:
        ...


class MapSceneManager(Protocol):
    """Collaborator for camera logic, overlays, and NPCs within a map scene."""

    active_sprite: CharacterMapSprite | None
    camera_offset: tuple[int, int]

    def update(self, delta_time: float, sprites: Sequence[CharacterMapSprite]) -> None:
        ...

    def render(self, renderer: Renderer) -> None:
        ...


class MapScene(Scene):
    """Tilemap-based scene coordinating characters and collisions."""

    background_color: Color = (0, 0, 0)

    def __init__(
        self,
        visual_tilemap: RenderableTilemapLayer,
        collision_tilemap: CollisionDetector | RenderableTilemapLayer,
        characters: Sequence[CharacterMapSprite],
        manager: MapSceneManager,
    ) -> None:
        self.visual_tilemap = visual_tilemap
        self.collision_tilemap = collision_tilemap
        self.characters = list(characters)
        self.manager = manager
        self._pressed_keys: set[str] = set()

        bounds = getattr(collision_tilemap, "pixel_size", None) or getattr(
            collision_tilemap, "size", None
        )
        for sprite in self.characters:
            sprite.collision_detector = collision_tilemap
            sprite.map_bounds = bounds

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        for event in events:
            if event.type == "QUIT":
                self.request_exit()
                continue

            key = None
            if event.payload:
                key = event.payload.get("key")
            if event.type == "KEYDOWN" and isinstance(key, str):
                self._pressed_keys.add(key)
            elif event.type == "KEYUP" and isinstance(key, str):
                self._pressed_keys.discard(key)

        active = self._active_sprite()
        if active:
            active.handle_input(set(self._pressed_keys))

    def update(self, delta_time: float) -> None:
        for sprite in self.characters:
            sprite.update(delta_time)
        self.manager.update(delta_time, self.characters)

    def render(self, renderer: Renderer) -> None:
        renderer.clear(self.background_color)
        camera_offset = getattr(self.manager, "camera_offset", (0, 0)) or (0, 0)

        self.visual_tilemap.render(renderer, camera_offset=camera_offset)
        for sprite in self.characters:
            sprite.render(renderer, camera_offset=camera_offset)
        self.manager.render(renderer)

    def _active_sprite(self) -> CharacterMapSprite | None:
        if getattr(self.manager, "active_sprite", None):
            return self.manager.active_sprite
        return self.characters[0] if self.characters else None
