"""Declarative map scene definitions and builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .map_scene_entities import NPC, PC
from .npc_controller import NPCController
from .sprites import PCMapSprite
from .spritesheet_declarative import SpriteSheet
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

    image: object
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
    """Declarative playable character definition."""

    starting: tuple[float, float]
    pc: type[PC]
    sprite: SpriteSheet


@dataclass(frozen=True)
class MapNPC:
    """Declarative NPC definition."""

    starting: tuple[float, float]
    npc: type[NPC]
    sprite: SpriteSheet


@dataclass(frozen=True)
class Map:
    """Declarative map definition for a tilemap scene.

    ``tiles`` is a grid of tile indices into ``tile_sheet``. Each integer refers
    to a tile in row-major order. ``None`` means no tile should be rendered for
    that cell; collision queries treat ``None`` as empty space. ``pc`` and
    ``npcs`` define the starting positions for the map entities.
    """

    tile_sheet: TileSheet
    tiles: Sequence[Sequence[int | None]]
    pc: MapPC
    npcs: Sequence[MapNPC] = field(default_factory=tuple)
    impassable_ids: set[int] = field(default_factory=set)
    tile_offsets: Sequence[Sequence[tuple[int, int] | None]] | None = None


@dataclass(frozen=True)
class MapSceneAssets:
    """Imperative objects built from a declarative map definition."""

    visual_tilemap: TilemapLayer
    collision_tilemap: TileCollisionDetector
    player: PCMapSprite
    npc_controllers: list[NPCController]


def build_map_scene_assets(definition: Map) -> MapSceneAssets:
    """Build the runtime objects needed to drive a map scene."""

    tileset = definition.tile_sheet.to_descriptor()
    visual_tilemap = TilemapLayer(
        tileset=tileset,
        tiles=definition.tiles,
        tile_offsets=definition.tile_offsets,
    )

    collision_tiles = _normalize_collision_tiles(definition.tiles)
    collision_map = Tilemap(
        tiles=collision_tiles,
        tile_size=(tileset.tile_width, tileset.tile_height),
        impassable_ids=set(definition.impassable_ids),
    )
    collision_tilemap = TileCollisionDetector(tilemap=collision_map)

    player = _build_player(definition.pc)
    npc_controllers = [_build_npc_controller(npc) for npc in definition.npcs]
    return MapSceneAssets(
        visual_tilemap=visual_tilemap,
        collision_tilemap=collision_tilemap,
        player=player,
        npc_controllers=npc_controllers,
    )


def _normalize_collision_tiles(
    tiles: Sequence[Sequence[int | None]],
) -> list[list[int]]:
    normalized: list[list[int]] = []
    for row in tiles:
        normalized.append([tile if tile is not None else -1 for tile in row])
    return normalized


def _build_player(definition: MapPC) -> PCMapSprite:
    player = definition.pc(definition.sprite)
    if not isinstance(player, PCMapSprite):
        raise TypeError("pc must construct a PCMapSprite instance")
    return player


def _build_npc_controller(definition: MapNPC) -> NPCController:
    controller = definition.npc(definition.sprite)
    if not isinstance(controller, NPCController):
        raise TypeError("npc must construct an NPCController instance")
    return controller
