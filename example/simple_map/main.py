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
from src.game.domain.npc_controller import NPCController, NPCRoute
from src.game.domain.scenes import MapScene
from src.game.domain.sprites import NPCMapSprite, PCMapSprite, SpriteSheetDescriptor
from src.game.domain.tilemap import TileCollisionDetector, Tilemap
from src.main import build_game
from src.game.infrastructure.assets import load_image

ASSETS_DIR = Path(__file__).parent / "assets"
TILE_SIZE = 32
MAP_DIMENSIONS = (50, 50)


# Asset helpers -------------------------------------------------------------

def load_asset(name: str, fallback_size: tuple[int, int], color: tuple[int, int, int]):
    """Load an image or build a placeholder surface when it is missing."""

    path = ASSETS_DIR / name
    return load_image(path, fallback_size, color)


def sprite_sheet(
    filename: str,
    frame_width: int,
    frame_height: int,
    *,
    columns: int,
    placeholder_color: tuple[int, int, int],
) -> SpriteSheetDescriptor:
    width = frame_width * columns
    height = frame_height * 4
    image = load_asset(filename, (width, height), placeholder_color)
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
    return SpriteSheetDescriptor(
        image=image,
        frame_width=frame_width,
        frame_height=frame_height,
        columns=columns,
        animations=animations,
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
        image=load_asset("tileset.png", (TILE_SIZE * 4, TILE_SIZE * 4), (60, 110, 170)),
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
        placeholder_color=(240, 220, 120),
    )
    return PCMapSprite(x=5 * TILE_SIZE, y=5 * TILE_SIZE, spritesheet=spritesheet, speed=140.0)


def create_patrolling_npc() -> NPCController:
    spritesheet = sprite_sheet(
        "npc_patrol.png",
        frame_width=TILE_SIZE,
        frame_height=TILE_SIZE,
        columns=4,
        placeholder_color=(160, 220, 255),
    )
    npc = NPCMapSprite(x=20 * TILE_SIZE, y=20 * TILE_SIZE, spritesheet=spritesheet, speed=80.0)

    span = 6 * TILE_SIZE
    route = NPCRoute(
        waypoints=[
            (npc.x, npc.y),
            (npc.x + span, npc.y),
            (npc.x + span, npc.y + span),
            (npc.x, npc.y + span),
        ],
        loop=True,
        wait_time=0.6,
    )
    return NPCController(npc=npc, route=route, speed=80.0)


def create_idle_npc() -> NPCController:
    spritesheet = sprite_sheet(
        "npc_idle.png",
        frame_width=TILE_SIZE,
        frame_height=TILE_SIZE,
        columns=4,
        placeholder_color=(200, 150, 255),
    )
    npc = NPCMapSprite(x=35 * TILE_SIZE, y=30 * TILE_SIZE, spritesheet=spritesheet, speed=0.0)
    route = NPCRoute(waypoints=[(npc.x, npc.y)], loop=True, wait_time=0.0)
    return NPCController(npc=npc, route=route, speed=0.0)


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
