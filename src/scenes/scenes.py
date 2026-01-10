"""Scene abstractions and example implementation.

This module defines the ``Scene`` base class along with ``UIScene`` and
tilemap-focused ``MapScene``/``MapSceneBase`` helpers. It also contains
``DemoScene`` for quick scaffolding and ``UIRenderer`` for turning UI layout
trees into renderer commands.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
import math
from asyncio import Future
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, Sequence

from ..core.contracts import Color, GameConfig, InputEvent, Key, Renderer
from ..world.map_scene_declarative import DebugCollisionLayer, Map, build_map_scene_assets
from ..world.npc_controller import NPCMapController
from ..world.sprites import NPCMapSprite, PCMapSprite, CollisionDetector
from ..world.tilemap_layer import TilemapLayer
from ..ui import (
    Border,
    Container,
    LayoutNode,
    MenuChoice,
    Rect,
    Text,
    UIElement,
    UIController,
)


class Scene(ABC):
    """Base class representing a game scene.

    Scenes orchestrate domain logic and describe what should be rendered without
    depending on a specific rendering framework.
    """

    background_color: Color = (0, 0, 0)
    _exit_requested: bool = False
    config: GameConfig = GameConfig()

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
        position = (
            (rect.x + rect.width // 2, rect.y + rect.height // 2)
            if text.center
            else (rect.x, rect.y)
        )
        renderer.draw_text(
            text.content,
            position,
            text.color,
            font_size=text.size,
            center=text.center,
        )

    def _render_menu_choice(
        self, renderer: Renderer, rect: Rect, choice: MenuChoice
    ) -> None:
        if choice.selected and choice.highlight_color:
            padding = max(choice.highlight_padding, 0)
            renderer.draw_rect(
                choice.highlight_color,
                (
                    rect.x - padding,
                    rect.y - padding,
                    rect.width + padding * 2,
                    rect.height + padding * 2,
                ),
            )
        position = (
            (rect.x + rect.width // 2, rect.y + rect.height // 2)
            if choice.center
            else (rect.x, rect.y)
        )
        renderer.draw_text(
            choice.display_label,
            position,
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
        self._ui_controller = UIController()
        self._pop_future: Future[None] | None = None

    @abstractmethod
    def build(self) -> UIElement:
        """Return the root UI element for the scene."""

    def update(self, delta_time: float) -> None:
        return None

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        root = self.build()
        self._ui_controller.handle_events(events, root)

    def pop(self) -> None:
        """Request the scene manager to remove this UI overlay."""
        from .utils import pop_ui

        pop_ui(self)

    def _set_pop_future(self, future: Future[None]) -> None:
        self._pop_future = future

    def _resolve_pop_future(self) -> None:
        if self._pop_future is None:
            return
        if not self._pop_future.done():
            self._pop_future.set_result(None)
        self._pop_future = None

    def render(self, renderer: Renderer) -> None:
        self.screen_size = renderer.size
        renderer.clear(self.background_color)
        root = self._ui_controller.apply(self.build())
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


class _OverlayRenderer:
    """Renderer proxy that disables clear calls for overlay scenes."""

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    @property
    def size(self) -> tuple[int, int]:
        return self._renderer.size

    def clear(self, color: Color) -> None:
        return None

    def draw_rect(self, color: Color, rect: tuple[int, int, int, int]) -> None:
        self._renderer.draw_rect(color, rect)

    def draw_rect_outline(
        self,
        color: Color,
        rect: tuple[int, int, int, int],
        width: int = 1,
    ) -> None:
        self._renderer.draw_rect_outline(color, rect, width=width)

    def draw_image(
        self,
        image: object,
        source_rect: tuple[int, int, int, int],
        destination: tuple[int, int],
    ) -> None:
        self._renderer.draw_image(image, source_rect, destination)

    def draw_text(
        self,
        text: str,
        position: tuple[int, int],
        color: Color,
        font_size: int = 32,
        center: bool = False,
    ) -> None:
        self._renderer.draw_text(
            text,
            position,
            color,
            font_size=font_size,
            center=center,
        )

    def present(self) -> None:
        self._renderer.present()


class LayeredScene(Scene):
    """Compose multiple scenes as layers.

    The ``scenes`` sequence is ordered top-to-bottom, so the last scene is the
    bottom layer. Input events and updates are forwarded to every scene in the
    provided order, while rendering happens from bottom-to-top so upper scenes
    overlay earlier layers. Only the bottom scene receives a real renderer; all
    overlay scenes get a renderer proxy whose ``clear`` method is a no-op to
    prevent wiping the canvas.
    """

    def __init__(self, scenes: Sequence[Scene]) -> None:
        self._scenes = list(scenes)
        self._overlay_renderer: _OverlayRenderer | None = None

    def on_enter(self) -> None:
        for scene in self._scenes:
            scene.config = self.config
            scene.on_enter()

    def on_exit(self) -> None:
        for scene in self._scenes:
            scene.on_exit()

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        for scene in self._scenes:
            scene.handle_events(events)

    def update(self, delta_time: float) -> None:
        for scene in self._scenes:
            scene.update(delta_time)

    def render(self, renderer: Renderer) -> None:
        if not self._scenes:
            return None
        overlay_renderer = self._overlay_renderer or _OverlayRenderer(renderer)
        self._overlay_renderer = overlay_renderer
        for index, scene in enumerate(reversed(self._scenes)):
            active_renderer = renderer if index == 0 else overlay_renderer
            scene.render(active_renderer)

    def should_exit(self) -> bool:
        return self._exit_requested or any(scene.should_exit() for scene in self._scenes)


class RenderableTilemapLayer(Protocol):
    """Renderable background or foreground tile layer."""

    pixel_size: tuple[int, int] | None

    def render(self, renderer: Renderer, camera_offset: tuple[int, int] = (0, 0)) -> None:
        ...


class RenderItem(Protocol):
    """Renderable item with a depth ordering value."""

    @property
    def render_order_y(self) -> float:
        ...

    def render(self, renderer: Renderer, camera_offset: tuple[int, int] = (0, 0)) -> None:
        ...


@dataclass(frozen=True)
class ObjectTileRenderItem:
    """Adapter for rendering a single object tile with depth ordering."""

    tilemap: TilemapLayer
    row: int
    column: int
    tile_id: int
    offset: tuple[int, int] = (0, 0)

    @property
    def render_order_y(self) -> float:
        tile_height = self.tilemap.tile_size[1]
        return self.row * tile_height + tile_height + self.offset[1]

    def render(self, renderer: Renderer, camera_offset: tuple[int, int] = (0, 0)) -> None:
        tile_width, tile_height = self.tilemap.tile_size
        camera_x, camera_y = camera_offset
        source_rect = self.tilemap._source_rect(self.tile_id)
        destination = (
            int(self.column * tile_width - camera_x + self.offset[0]),
            int(self.row * tile_height - camera_y + self.offset[1]),
        )
        renderer.draw_image(self.tilemap.tileset.image, source_rect, destination)


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
        object_tilemap: RenderableTilemapLayer | None = None,
        npc_controllers: Sequence[NPCMapController] | None = None,
        base_collision_layer: DebugCollisionLayer | None = None,
        object_collision_layer: DebugCollisionLayer | None = None,
        on_coordinate: Mapping[
            tuple[int, int],
            Callable[[MapScene, tuple[int, int]], None],
        ]
        | None = None,
    ) -> None:
        self.visual_tilemap = visual_tilemap
        self.object_tilemap = object_tilemap
        self.collision_tilemap = collision_tilemap
        self.player = player
        self.npc_controllers = list(npc_controllers or [])
        self.base_collision_layer = base_collision_layer
        self.object_collision_layer = object_collision_layer
        self._npc_sprites: list[NPCMapSprite] = [c.npc for c in self.npc_controllers if c.npc]
        self._pressed_keys: set[str] = set()
        self._interaction_in_progress = False
        self._interaction_task: asyncio.Task[None] | None = None
        self._on_coordinate = dict(on_coordinate or {})
        self._last_tile_coordinate: tuple[int, int] | None = None
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
        self._wire_sprite_colliders()

    def _wire_sprite_colliders(self) -> None:
        self.player.sprite_colliders = lambda: [
            npc.hitbox for npc in self._npc_sprites if npc.sprite_colliders is not None
        ]
        for npc in self._npc_sprites:
            npc.sprite_colliders = lambda npc=npc: [
                self.player.hitbox,
                *[
                    other.hitbox
                    for other in self._npc_sprites
                    if other is not npc and other.sprite_colliders is not None
                ],
            ]

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

            if self._interaction_in_progress:
                continue

            key = None
            if event.payload:
                key = event.payload.get("key")
            if event.type == "KEYDOWN" and isinstance(key, str):
                self._pressed_keys.add(key)
            elif event.type == "KEYUP" and isinstance(key, str):
                self._pressed_keys.discard(key)

        if self._interaction_in_progress:
            return

        if any(
            event.type == "KEYDOWN"
            and event.payload
            and event.payload.get("key") == Key.ENTER
            for event in events
        ):
            controller = self._find_interactable_controller()
            if controller:
                self._pressed_keys.clear()
                self._interaction_in_progress = True
                from .utils import get_scheduler

                scheduler = get_scheduler()
                self._interaction_task = scheduler.create_task(
                    controller.interact(self.player)
                )
                self._interaction_task.add_done_callback(self._resolve_interaction_task)
                return

        self.player.handle_input(set(self._pressed_keys))

    def update(self, delta_time: float) -> None:
        if self._interaction_in_progress:
            return

        for controller in self.npc_controllers:
            controller.update(delta_time, self.player)
        for sprite in self._all_sprites():
            sprite.update(delta_time)
        self._handle_on_coordinate()

    def _resolve_interaction_task(self, task: asyncio.Task[None]) -> None:
        if self._interaction_task is not task:
            return

        self._interaction_task = None
        self._interaction_in_progress = False
        try:
            task.result()
        except Exception:
            return None

    def _handle_on_coordinate(self) -> None:
        if not self._on_coordinate:
            return
        coordinate = self._player_tile_coordinate()
        if coordinate is None or coordinate == self._last_tile_coordinate:
            return
        self._last_tile_coordinate = coordinate
        handler = self._on_coordinate.get(coordinate)
        if handler:
            handler(self, coordinate)

    def _player_tile_coordinate(self) -> tuple[int, int] | None:
        """Return the player's (row, column) tile using the hitbox feet position."""

        tile_size = self._resolve_tile_size()
        if tile_size is None:
            return None
        tile_width, tile_height = tile_size
        if tile_width <= 0 or tile_height <= 0:
            return None

        x, y, width, height = self.player.hitbox
        sample_x = x + width * 0.5
        sample_y = math.nextafter(y + height, -math.inf)
        row = int(sample_y // tile_height)
        column = int(sample_x // tile_width)
        return (row, column)

    def _resolve_tile_size(self) -> tuple[int, int] | None:
        if hasattr(self.visual_tilemap, "tile_size"):
            return self.visual_tilemap.tile_size
        if hasattr(self.collision_tilemap, "tilemap"):
            tilemap = getattr(self.collision_tilemap, "tilemap", None)
            if tilemap and hasattr(tilemap, "tile_size"):
                return tilemap.tile_size
        if hasattr(self.collision_tilemap, "tile_size"):
            return self.collision_tilemap.tile_size
        return None

    def render(self, renderer: Renderer) -> None:
        renderer.clear(self.background_color)
        self.camera.set_view_size(renderer.size)
        self.camera.follow(self.player.hitbox)
        camera_offset = self.camera.offset

        self.visual_tilemap.render(renderer, camera_offset=camera_offset)
        render_items: list[RenderItem] = []
        if isinstance(self.object_tilemap, TilemapLayer):
            render_items.extend(
                self._object_tile_render_items(
                    self.object_tilemap, renderer, camera_offset
                )
            )
        elif self.object_tilemap is not None:
            self.object_tilemap.render(renderer, camera_offset=camera_offset)
        render_items.extend(self._all_sprites())
        for item in sorted(render_items, key=lambda item: item.render_order_y):
            item.render(renderer, camera_offset=camera_offset)
        if self.config.debug_collision:
            self._render_collision_debug(renderer, camera_offset)
            for sprite in self._all_sprites():
                if not hasattr(sprite, "hitbox"):
                    continue
                hitbox = sprite.hitbox
                rect = (
                    int(hitbox[0] - camera_offset[0]),
                    int(hitbox[1] - camera_offset[1]),
                    int(hitbox[2]),
                    int(hitbox[3]),
                )
                renderer.draw_rect_outline((255, 0, 0), rect)

    def _render_collision_debug(
        self, renderer: Renderer, camera_offset: tuple[int, int]
    ) -> None:
        if self.base_collision_layer:
            self._render_collision_layer(
                renderer,
                camera_offset,
                self.base_collision_layer,
                color=(255, 165, 0),
            )
        if self.object_collision_layer:
            self._render_collision_layer(
                renderer,
                camera_offset,
                self.object_collision_layer,
                color=(0, 200, 255),
            )

    def _render_collision_layer(
        self,
        renderer: Renderer,
        camera_offset: tuple[int, int],
        layer: DebugCollisionLayer,
        color: Color,
    ) -> None:
        tile_width, tile_height = layer.tile_size
        if tile_width <= 0 or tile_height <= 0:
            return

        tiles = layer.tiles
        rows = len(tiles)
        columns = len(tiles[0]) if rows else 0
        if rows == 0 or columns == 0:
            return

        view_width, view_height = renderer.size
        camera_x, camera_y = camera_offset
        start_column = max(0, int(camera_x // tile_width))
        end_column = min(columns, int((camera_x + view_width + tile_width - 1) // tile_width))
        start_row = max(0, int(camera_y // tile_height))
        end_row = min(rows, int((camera_y + view_height + tile_height - 1) // tile_height))

        for row in range(start_row, end_row):
            tile_row = tiles[row]
            for column in range(start_column, end_column):
                tile_id = tile_row[column]
                if tile_id is None or tile_id not in layer.impassable_ids:
                    continue
                rect = (
                    int(column * tile_width - camera_x),
                    int(row * tile_height - camera_y),
                    int(tile_width),
                    int(tile_height),
                )
                renderer.draw_rect_outline(color, rect)

    def _object_tile_render_items(
        self,
        tilemap: TilemapLayer,
        renderer: Renderer,
        camera_offset: tuple[int, int],
    ) -> list[ObjectTileRenderItem]:
        tile_width, tile_height = tilemap.tile_size
        if tile_width <= 0 or tile_height <= 0:
            return []

        rows = len(tilemap.tiles)
        columns = len(tilemap.tiles[0]) if rows else 0
        if rows == 0 or columns == 0:
            return []

        view_width, view_height = renderer.size
        camera_x, camera_y = camera_offset
        start_column = max(0, int(camera_x // tile_width))
        end_column = min(columns, int((camera_x + view_width + tile_width - 1) // tile_width))
        start_row = max(0, int(camera_y // tile_height))
        end_row = min(rows, int((camera_y + view_height + tile_height - 1) // tile_height))

        items: list[ObjectTileRenderItem] = []
        for row in range(start_row, end_row):
            tile_row = tilemap.tiles[row]
            offset_row = (
                tilemap.tile_offsets[row]
                if tilemap.tile_offsets and row < len(tilemap.tile_offsets)
                else None
            )
            for column in range(start_column, end_column):
                tile_id = tile_row[column]
                if tile_id is None or tile_id < 0:
                    continue

                offset = (0, 0)
                if offset_row and column < len(offset_row) and offset_row[column]:
                    offset = offset_row[column]  # type: ignore[assignment]
                items.append(
                    ObjectTileRenderItem(
                        tilemap=tilemap,
                        row=row,
                        column=column,
                        tile_id=tile_id,
                        offset=offset,
                    )
                )
        return items

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


class MapSceneBase(MapScene, ABC):
    """Declarative map scene base that builds map assets from definitions."""

    @abstractmethod
    def build(self) -> Map:
        """Return the declarative map definition for this scene."""

    def __init__(self) -> None:
        definition = self.build()
        assets = build_map_scene_assets(definition)
        super().__init__(
            visual_tilemap=assets.visual_tilemap,
            object_tilemap=assets.object_tilemap,
            collision_tilemap=assets.collision_tilemap,
            player=assets.player,
            npc_controllers=assets.npc_controllers,
            base_collision_layer=assets.base_collision_layer,
            object_collision_layer=assets.object_collision_layer,
            on_coordinate=assets.on_coordinate,
        )


def _intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)
