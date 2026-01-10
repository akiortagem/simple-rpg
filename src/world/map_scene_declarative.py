"""Declarative map scene definitions and builders.

Define ``Map``, ``MapPC``, ``MapNPC``, and ``TileSheet`` data objects here, then
call ``build_map_scene_assets`` to turn them into runtime sprites and
``TilemapLayer`` instances for ``MapScene``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .map_scene_entities import NPC
from .npc_controller import NPCController
from .sprites import PCMapSprite
from .tilemap import TileCollisionDetector, Tilemap
from .tilemap_layer import TilemapLayer, TilesetDescriptor


@dataclass(frozen=True)
class TileSheet:
    """Declarative tile sheet descriptor.

    ``tile_width``/``tile_height`` describe the size (in pixels) of each tile.
    ``columns`` indicates how many tiles appear in each row; tile indices in the
    map ``tiles`` grid are integers that reference tiles in this sheet in
    row-major order (left-to-right, then top-to-bottom).
    """

    image: str | Path
    tile_width: int
    tile_height: int
    columns: int

    def to_descriptor(self) -> TilesetDescriptor:
        return TilesetDescriptor(
            image=self.image,
            tile_width=self.tile_width,
            tile_height=self.tile_height,
            columns=self.columns,
        )


@dataclass(frozen=True)
class MapPC:
    """Declarative playable character definition.

    ``starting`` is provided in tile coordinates (row, column).
    """

    starting: tuple[int, int]
    pc: PCMapSprite


@dataclass(frozen=True)
class MapNPC:
    """Declarative NPC definition.

    ``starting`` is provided in tile coordinates (row, column).
    """

    starting: tuple[int, int]
    npc: NPC


@dataclass(frozen=True)
class Map:
    """Declarative map definition for a tilemap scene.

    ``tiles`` is a grid of tile indices into ``tile_sheet``. Each integer refers
    to a tile in row-major order. ``None`` means no tile should be rendered for
    that cell; collision queries treat ``None`` as empty space. ``pc`` and
    ``npcs`` define the starting positions for the map entities, expressed as
    tile coordinates (row, column).

    Use ``object_tiles`` to supply a second tile layer (same dimensions as
    ``tiles``) that is rendered after the base tiles but before sprites. Use
    ``0`` in ``object_tiles`` for empty space, and provide an ``object_tilesheet``
    describing the artwork. Any non-zero object tile IDs listed in
    ``impassable_object_ids`` will block movement alongside
    ``impassable_ids``.

    ``on_coordinate`` maps tile coordinates (row, column) to callbacks invoked
    as ``handler(scene, (row, column))`` when the player enters the tile.
    """

    tile_sheet: TileSheet
    tiles: Sequence[Sequence[int | None]]
    pc: MapPC
    npcs: Sequence[MapNPC] = field(default_factory=tuple)
    impassable_ids: set[int] = field(default_factory=set)
    object_tiles: Sequence[Sequence[int]] | None = None
    object_tilesheet: TileSheet | None = None
    impassable_object_ids: set[int] = field(default_factory=set)
    tile_offsets: Sequence[Sequence[tuple[int, int] | None]] | None = None
    on_coordinate: Mapping[tuple[int, int], Callable[..., None]] | None = None


@dataclass(frozen=True)
class DebugCollisionLayer:
    """Collision metadata for debugging per tile layer."""

    tiles: Sequence[Sequence[int | None]]
    tile_size: tuple[int, int]
    impassable_ids: set[int]


@dataclass(frozen=True)
class MapSceneAssets:
    """Imperative objects built from a declarative map definition."""

    visual_tilemap: TilemapLayer
    object_tilemap: TilemapLayer | None
    collision_tilemap: TileCollisionDetector
    base_collision_layer: DebugCollisionLayer | None
    object_collision_layer: DebugCollisionLayer | None
    player: PCMapSprite
    npc_controllers: list[NPCController]
    on_coordinate: Mapping[tuple[int, int], Callable[..., None]] | None


def build_map_scene_assets(definition: Map) -> MapSceneAssets:
    """Build the runtime objects needed to drive a map scene."""

    tileset = definition.tile_sheet.to_descriptor()
    visual_tilemap = TilemapLayer(
        tileset=tileset,
        tiles=definition.tiles,
        tile_offsets=definition.tile_offsets,
    )

    object_tilemap = _build_object_tilemap(definition)
    collision_tiles = _build_collision_tiles(definition.tiles, definition)
    collision_map = Tilemap(
        tiles=collision_tiles,
        tile_size=(tileset.tile_width, tileset.tile_height),
        impassable_ids={1},
    )
    collision_tilemap = TileCollisionDetector(tilemap=collision_map)

    tile_size = (tileset.tile_width, tileset.tile_height)
    player = _build_player(definition.pc, tile_size)
    npc_controllers = [
        _build_npc_controller(npc, tile_size) for npc in definition.npcs
    ]
    base_collision_layer = DebugCollisionLayer(
        tiles=definition.tiles,
        tile_size=(tileset.tile_width, tileset.tile_height),
        impassable_ids=definition.impassable_ids,
    )
    object_collision_layer = None
    if definition.object_tiles and definition.object_tilesheet:
        object_collision_layer = DebugCollisionLayer(
            tiles=definition.object_tiles,
            tile_size=(
                definition.object_tilesheet.tile_width,
                definition.object_tilesheet.tile_height,
            ),
            impassable_ids=definition.impassable_object_ids,
        )
    return MapSceneAssets(
        visual_tilemap=visual_tilemap,
        object_tilemap=object_tilemap,
        collision_tilemap=collision_tilemap,
        base_collision_layer=base_collision_layer,
        object_collision_layer=object_collision_layer,
        player=player,
        npc_controllers=npc_controllers,
        on_coordinate=definition.on_coordinate,
    )


def _build_collision_tiles(
    tiles: Sequence[Sequence[int | None]],
    definition: Map,
) -> list[list[int]]:
    normalized: list[list[int]] = []
    object_tiles = definition.object_tiles
    for row_index, row in enumerate(tiles):
        object_row = object_tiles[row_index] if object_tiles else None
        normalized_row: list[int] = []
        for column_index, tile in enumerate(row):
            base_blocking = tile is not None and tile in definition.impassable_ids
            object_tile = object_row[column_index] if object_row else 0
            object_blocking = (
                object_tile != 0 and object_tile in definition.impassable_object_ids
            )
            normalized_row.append(1 if base_blocking or object_blocking else -1)
        normalized.append(normalized_row)
    return normalized


def _build_object_tilemap(definition: Map) -> TilemapLayer | None:
    if definition.object_tiles is None:
        return None
    if definition.object_tilesheet is None:
        raise ValueError("object_tilesheet is required when object_tiles are provided")
    _ensure_object_tiles_shape(definition.tiles, definition.object_tiles)
    return TilemapLayer(
        tileset=definition.object_tilesheet.to_descriptor(),
        tiles=definition.object_tiles,
    )


def _ensure_object_tiles_shape(
    tiles: Sequence[Sequence[int | None]],
    object_tiles: Sequence[Sequence[int]],
) -> None:
    if len(tiles) != len(object_tiles):
        raise ValueError("object_tiles must match the row count of tiles")
    if tiles and object_tiles:
        expected_columns = len(tiles[0])
        for row in object_tiles:
            if len(row) != expected_columns:
                raise ValueError("object_tiles must match the column count of tiles")


def _build_player(definition: MapPC, tile_size: tuple[int, int]) -> PCMapSprite:
    template = definition.pc
    if not isinstance(template, PCMapSprite):
        raise TypeError("pc must construct a PCMapSprite instance")
    player = _clone_player(template)
    player.x, player.y = _tile_to_pixels(definition.starting, tile_size)
    return player


def _build_npc_controller(
    definition: MapNPC,
    tile_size: tuple[int, int],
) -> NPCController:
    npc = definition.npc
    if not isinstance(npc, NPC):
        raise TypeError("npc must construct an NPC instance")
    controller = NPCController(actor=npc)
    if controller.npc is None:
        raise TypeError("npc must construct an NPCController with an NPCMapSprite")
    controller.npc.x, controller.npc.y = _tile_to_pixels(definition.starting, tile_size)
    return controller


def _tile_to_pixels(
    starting: tuple[int, int],
    tile_size: tuple[int, int],
) -> tuple[float, float]:
    start_row, start_column = starting
    tile_width, tile_height = tile_size
    return (start_column * tile_width, start_row * tile_height)


def _clone_player(template: PCMapSprite) -> PCMapSprite:
    return PCMapSprite(
        name=template.name,
        x=0.0,
        y=0.0,
        spritesheet=template.spritesheet,
        speed=template.speed,
        frame_duration=template.frame_duration,
        current_action=template.current_action,
        current_direction=template.current_direction,
        hitbox_size=template.hitbox_size,
        hitbox_offset=template.hitbox_offset,
    )
