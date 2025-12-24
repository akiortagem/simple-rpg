"""Scene abstractions and example implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Sequence

from .contracts import Color, InputEvent, Key, Renderer
from .npc_controller import NPCMapController
from .sprites import NPCMapSprite, PCMapSprite, CollisionDetector
from .ui import (
    Border,
    Container,
    LayoutNode,
    MenuChoice,
    Rect,
    Text,
    UIElement,
)


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


class UIRenderer:
    """Render UI layout trees into renderer draw calls."""

    def render(self, renderer: Renderer, layout: LayoutNode) -> None:
        self._render_node(renderer, layout)

    def _render_node(self, renderer: Renderer, node: LayoutNode) -> None:
        element = node.element
        if isinstance(element, Container):
            self._render_container(renderer, node.rect, element)
        elif isinstance(element, Border):
            self._render_border(renderer, node.rect, element)
        elif isinstance(element, Text):
            self._render_text(renderer, node.rect, element)
        elif isinstance(element, MenuChoice):
            self._render_menu_choice(renderer, node.rect, element)
        for child in node.children:
            self._render_node(renderer, child)

    def _render_container(
        self, renderer: Renderer, rect: Rect, container: Container
    ) -> None:
        renderer.draw_rect(
            container.background_color, (rect.x, rect.y, rect.width, rect.height)
        )

    def _render_border(self, renderer: Renderer, rect: Rect, border: Border) -> None:
        width = min(border.width, rect.width, rect.height)
        if width <= 0:
            return
        renderer.draw_rect(border.color, (rect.x, rect.y, rect.width, width))
        renderer.draw_rect(
            border.color,
            (rect.x, rect.y + rect.height - width, rect.width, width),
        )
        renderer.draw_rect(border.color, (rect.x, rect.y, width, rect.height))
        renderer.draw_rect(
            border.color,
            (rect.x + rect.width - width, rect.y, width, rect.height),
        )

    def _render_text(self, renderer: Renderer, rect: Rect, text: Text) -> None:
        renderer.draw_text(
            text.content,
            (rect.x, rect.y),
            text.color,
            font_size=text.size,
            center=text.center,
        )

    def _render_menu_choice(
        self, renderer: Renderer, rect: Rect, choice: MenuChoice
    ) -> None:
        renderer.draw_text(
            choice.display_label,
            (rect.x, rect.y),
            choice.display_color,
            font_size=choice.size,
            center=choice.center,
        )


class UIScene(Scene):
    """Scene base class for declarative UI layouts."""

    background_color: Color = (0, 0, 0)

    def __init__(self) -> None:
        self.screen_size = (0, 0)
        self._ui_renderer = UIRenderer()

    @abstractmethod
    def build(self) -> UIElement:
        """Return the root UI element for the scene."""

    def update(self, delta_time: float) -> None:
        return None

    def render(self, renderer: Renderer) -> None:
        self.screen_size = renderer.size
        renderer.clear(self.background_color)
        root = self.build()
        layout = root.layout(Rect(0, 0, self.screen_size[0], self.screen_size[1]))
        self._ui_renderer.render(renderer, layout)


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


class MapCamera:
    """Camera that tracks a target and allows manual panning."""

    def __init__(self, map_size: tuple[int, int] | None = None) -> None:
        self.map_size = map_size
        self.view_size: tuple[int, int] | None = None
        self._manual_offset: tuple[float, float] = (0.0, 0.0)
        self._position: tuple[float, float] = (0.0, 0.0)

    @property
    def offset(self) -> tuple[int, int]:
        return int(self._position[0]), int(self._position[1])

    def set_map_size(self, map_size: tuple[int, int] | None) -> None:
        self.map_size = map_size
        self._clamp_to_bounds()

    def set_view_size(self, view_size: tuple[int, int]) -> None:
        self.view_size = view_size
        self._clamp_to_bounds()

    def pan(self, dx: float, dy: float) -> None:
        self._manual_offset = (
            self._manual_offset[0] + dx,
            self._manual_offset[1] + dy,
        )
        self._position = (
            self._position[0] + dx,
            self._position[1] + dy,
        )
        self._clamp_to_bounds()

    def pan_route(self, deltas: Sequence[tuple[float, float]]) -> None:
        """Follow a series of pan deltas while respecting map bounds."""

        for dx, dy in deltas:
            self.pan(dx, dy)

    def follow(self, target_hitbox: tuple[float, float, float, float]) -> None:
        if not self.view_size:
            return

        tx, ty, tw, th = target_hitbox
        desired_x = tx + tw * 0.5 - self.view_size[0] * 0.5 + self._manual_offset[0]
        desired_y = ty + th * 0.5 - self.view_size[1] * 0.5 + self._manual_offset[1]

        self._position = (desired_x, desired_y)
        self._clamp_to_bounds()

    def _clamp_to_bounds(self) -> None:
        if not self.map_size or not self.view_size:
            return

        max_x = max(self.map_size[0] - self.view_size[0], 0)
        max_y = max(self.map_size[1] - self.view_size[1], 0)

        clamped_x = min(max(self._position[0], 0.0), max_x)
        clamped_y = min(max(self._position[1], 0.0), max_y)
        self._position = (clamped_x, clamped_y)


class MapScene(Scene):
    """Tilemap-based scene coordinating characters and collisions."""

    background_color: Color = (0, 0, 0)

    def __init__(
        self,
        visual_tilemap: RenderableTilemapLayer,
        collision_tilemap: CollisionDetector | RenderableTilemapLayer,
        player: PCMapSprite,
        npc_controllers: Sequence[NPCMapController] | None = None,
    ) -> None:
        self.visual_tilemap = visual_tilemap
        self.collision_tilemap = collision_tilemap
        self.player = player
        self.npc_controllers = list(npc_controllers or [])
        self._npc_sprites: list[NPCMapSprite] = [c.npc for c in self.npc_controllers if c.npc]
        self._pressed_keys: set[str] = set()
        self.camera = MapCamera()

        collision_detector = (
            collision_tilemap if hasattr(collision_tilemap, "collides") else None
        )
        bounds_source = collision_detector or collision_tilemap
        bounds = getattr(bounds_source, "pixel_size", None) or getattr(
            bounds_source, "size", None
        )
        self.camera.set_map_size(bounds)
        for sprite in self._all_sprites():
            sprite.collision_detector = collision_detector
            sprite.map_bounds = bounds

    def on_enter(self) -> None:
        for controller in self.npc_controllers:
            controller.on_enter()

    def on_exit(self) -> None:
        for controller in self.npc_controllers:
            controller.on_exit()

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

        self.player.handle_input(set(self._pressed_keys))
        if any(event.type == "KEYDOWN" and event.payload and event.payload.get("key") == Key.ENTER for event in events):
            controller = self._find_interactable_controller()
            if controller:
                controller.interact(self.player)

    def update(self, delta_time: float) -> None:
        for controller in self.npc_controllers:
            controller.update(delta_time, self.player)
        for sprite in self._all_sprites():
            sprite.update(delta_time)

    def render(self, renderer: Renderer) -> None:
        renderer.clear(self.background_color)
        self.camera.set_view_size(renderer.size)
        self.camera.follow(self.player.hitbox)
        camera_offset = self.camera.offset

        self.visual_tilemap.render(renderer, camera_offset=camera_offset)
        for sprite in self._all_sprites():
            sprite.render(renderer, camera_offset=camera_offset)

    def pan_camera(self, dx: float, dy: float) -> None:
        """Shift the camera by the given delta without exposing renderer details."""

        self.camera.pan(dx, dy)

    def pan_camera_route(self, deltas: Sequence[tuple[float, float]]) -> None:
        """Apply a sequence of camera deltas in one call."""

        self.camera.pan_route(deltas)

    def _all_sprites(self) -> list[PCMapSprite | NPCMapSprite]:
        return [self.player, *self._npc_sprites]

    def _find_interactable_controller(self) -> NPCMapController | None:
        player_hitbox = self.player.hitbox
        reach = max(self.player.spritesheet.frame_width, self.player.spritesheet.frame_height) * 0.5
        x, y, width, height = player_hitbox

        if self.player.facing_direction == "left":
            zone = (x - reach, y, reach, height)
        elif self.player.facing_direction == "right":
            zone = (x + width, y, reach, height)
        elif self.player.facing_direction == "up":
            zone = (x, y - reach, width, reach)
        else:  # down
            zone = (x, y + height, width, reach)

        for controller in self.npc_controllers:
            if controller.npc is None:
                continue
            npc_hitbox = controller.npc.hitbox
            if _intersects(zone, npc_hitbox):
                return controller

        return None


def _intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)
