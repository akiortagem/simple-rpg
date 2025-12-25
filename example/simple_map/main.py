"""Simple 50x50 overworld example with a patrol and idle NPC.

Asset filenames expected by this example:
- assets/tileset.png
- assets/player.png
- assets/npc_patrol.png
- assets/npc_idle.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.game.domain import TilesetDescriptor, TilemapLayer
from src.game.domain.map_scene_entities import NPC
from src.game.domain.npc_routes import LoopRoute, NPCRoute, Route
from src.game.domain.npc_controller import NPCController
from src.game.domain.scenes import MapScene
from src.game.domain.sprites import PCMapSprite
from src.game.domain.spritesheet_declarative import SpriteSheet, SpriteSheetAnimations
from src.game.domain.tilemap import TileCollisionDetector, Tilemap
from src.game.domain.ui_kit import show_dialog
from src.main import build_game

ASSETS_DIR = Path(__file__).parent / "assets"
TILE_SIZE = 32
MAP_DIMENSIONS = (50, 50)


def sprite_sheet(
    filename: str,
    frame_width: int,
    frame_height: int,
    *,
    columns: int,
) -> SpriteSheet:
    image = ASSETS_DIR / filename
    animations = {
        "idle": {
            "down": [0],
            "left": [4],
            "right": [8],
            "up": [12],
        },
        "walk": {
            "down": [0, 1, 2, 3],
            "left": [4, 5, 6, 7],
            "right": [8, 9, 10, 11],
            "up": [12, 13, 14, 15],
        },
    }
    return SpriteSheet(
        image=image,
        frame_width=frame_width,
        frame_height=frame_height,
        columns=columns,
        animations=SpriteSheetAnimations(actions=animations),
    )


# World construction --------------------------------------------------------

def build_ground_layer() -> tuple[TilemapLayer, TileCollisionDetector]:
    rows, columns = MAP_DIMENSIONS
    base_row: list[int] = [0] * columns
    tiles: list[list[int]] = []

    for row in range(rows):
        row_tiles = base_row.copy()
        for column in range(columns):
            if row in {0, rows - 1} or column in {0, columns - 1}:
                row_tiles[column] = 1
            elif (row + column) % 13 == 0:
                row_tiles[column] = 2
        tiles.append(row_tiles)

    tileset = TilesetDescriptor(
        image=ASSETS_DIR / "tileset.png",
        tile_width=TILE_SIZE,
        tile_height=TILE_SIZE,
        columns=4,
    )

    visual_layer = TilemapLayer(tileset=tileset, tiles=tiles)

    collision_map = Tilemap(tiles=tiles, tile_size=(TILE_SIZE, TILE_SIZE), impassable_ids={1})
    collision_detector = TileCollisionDetector(tilemap=collision_map)
    return visual_layer, collision_detector


def create_player() -> PCMapSprite:
    spritesheet = sprite_sheet(
        "player.png",
        frame_width=TILE_SIZE,
        frame_height=TILE_SIZE,
        columns=4,
    )
    return PCMapSprite(
        x=5 * TILE_SIZE,
        y=5 * TILE_SIZE,
        spritesheet=spritesheet.to_descriptor(),
        speed=140.0,
    )


class PatrollingNPC(NPC):
    def __init__(self, spritesheet: SpriteSheet, *, start: tuple[float, float]) -> None:
        super().__init__(spritesheet)
        self._start = start

    def patrol(self) -> Route | None:
        span = 6 * TILE_SIZE
        start_x, start_y = self._start
        return LoopRoute(
            waypoints=[
                (start_x, start_y),
                (start_x + span, start_y),
                (start_x + span, start_y + span),
                (start_x, start_y + span),
            ],
            wait_time=0.6,
        )

    def interact(self, player: PCMapSprite) -> None:
        show_dialog("The patrol keeps marching along.")


class IdleNPC(NPC):
    def patrol(self) -> Route | None:
        return NPCRoute(waypoints=(), loop=True, wait_time=0.0)

    def interact(self, player: PCMapSprite) -> None:
        show_dialog("The idle NPC smiles politely.")


def create_patrolling_npc() -> NPCController:
    spritesheet = sprite_sheet(
        "npc_patrol.png",
        frame_width=TILE_SIZE,
        frame_height=TILE_SIZE,
        columns=4,
    )
    start = (20 * TILE_SIZE, 20 * TILE_SIZE)
    npc = PatrollingNPC(spritesheet, start=start)
    controller = NPCController(actor=npc, speed=80.0)
    if controller.npc is not None:
        controller.npc.x, controller.npc.y = start
    return controller


def create_idle_npc() -> NPCController:
    spritesheet = sprite_sheet(
        "npc_idle.png",
        frame_width=TILE_SIZE,
        frame_height=TILE_SIZE,
        columns=4,
    )
    start = (35 * TILE_SIZE, 30 * TILE_SIZE)
    npc = IdleNPC(spritesheet)
    controller = NPCController(actor=npc, speed=0.0)
    if controller.npc is not None:
        controller.npc.x, controller.npc.y = start
    return controller


# Entry point ---------------------------------------------------------------

def main() -> None:
    visual_layer, collision_detector = build_ground_layer()
    player = create_player()
    controllers: Sequence[NPCController] = [create_patrolling_npc(), create_idle_npc()]

    scene = MapScene(
        visual_tilemap=visual_layer,
        collision_tilemap=collision_detector,
        player=player,
        npc_controllers=controllers,
    )

    game = build_game(title="Simple RPG - Simple Map", initial_scene=scene)
    game.run()


if __name__ == "__main__":
    main()
