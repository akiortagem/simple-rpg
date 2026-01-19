"""Simple 10x10 overworld example with a patrol and idle NPC.

Asset filenames expected by this example:
- assets/tileset.png
- assets/player.png
- assets/npc_patrol.png
- assets/npc_idle.png
"""

from __future__ import annotations

from pathlib import Path

from src.scenes.scenes import MapSceneBase
from src.world.map_scene_entities import PC
from src.world.map_scene_declarative import Map, MapNPC, MapPC, TileSheet
from src.world.spritesheet_declarative import SpriteSheet, SpriteSheetAnimations
from src.main import build_game

from .npcs import PatrollingNPC, IdleNPC

ASSETS_DIR = Path(__file__).parent.parent / "common_assets"
TILE_SIZE = 32
SPRITE_TILE_SIZE = 64


SPRITE_ANIMATIONS = SpriteSheetAnimations(
    actions={
        "idle": {
            "down": [19],
            "left": [12],
            "right": [30],
            "up": [0],
        },
        "walk": {
            "down": [18, 19, 20, 21, 22, 23, 24, 25, 26],
            "left": [9, 10, 11, 12, 13, 14, 15, 16, 17],
            "right": [27, 28, 29, 30, 31, 32, 33, 34, 35],
            "up": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        },
    },
)

PLAYER_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "player.png",
    frame_width=SPRITE_TILE_SIZE,
    frame_height=SPRITE_TILE_SIZE,
    columns=9,
    animations=SPRITE_ANIMATIONS,
)

PATROL_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "npc_patrol.png",
    frame_width=SPRITE_TILE_SIZE,
    frame_height=SPRITE_TILE_SIZE,
    columns=9,
    animations=SPRITE_ANIMATIONS,
)

IDLE_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "npc_idle.png",
    frame_width=SPRITE_TILE_SIZE,
    frame_height=SPRITE_TILE_SIZE,
    columns=9,
    animations=SPRITE_ANIMATIONS,
)


# World construction --------------------------------------------------------

MAP_SIZE = 10

HITBOX_SIZE = (25, 25)
HITBOX_OFFSET = (20, 43)


class PlayerPC(PC):
    name = "Player"
    speed = 140.0
    hitbox_size = HITBOX_SIZE
    hitbox_offset = HITBOX_OFFSET


class SimpleMapScene(MapSceneBase):
    def __init__(self) -> None:
        super().__init__()
        for controller in self.npc_controllers:
            if isinstance(controller.actor, PatrollingNPC):
                controller.speed = 80.0
                if controller.npc is not None:
                    controller.npc.speed = 80.0
            elif isinstance(controller.actor, IdleNPC):
                controller.speed = 0.0
                if controller.npc is not None:
                    controller.npc.speed = 0.0

    def build(self) -> Map:
        tiles = [
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 56, 1, 1, 1, 1],
        ]
        tile_sheet = TileSheet(
            image=ASSETS_DIR / "tileset.png",
            tile_width=TILE_SIZE,
            tile_height=TILE_SIZE,
            columns=8,
        )

        object_tiles = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 0, 7, 7, 7, 7, 7, 7, 7, 7],
            [23, 0, 23, 23, 23, 23, 23, 23, 23, 23],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 7, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 23, 0, 0],
        ]

        object_tilesheet = TileSheet(
            image=ASSETS_DIR / "objects_tilesheet.png",
            tile_width=TILE_SIZE,
            tile_height=TILE_SIZE,
            columns=16,
        )

        impassable_object_ids={23}

        return Map(
            tile_sheet=tile_sheet,
            tiles=tiles,
            pc=MapPC(
                starting=(2, 2),
                pc=PlayerPC(PLAYER_SPRITESHEET),
            ),
            object_tiles=object_tiles,
            object_tilesheet=object_tilesheet,
            impassable_object_ids=impassable_object_ids,
            npcs=(
                MapNPC(
                    starting=(2, 7),
                    npc=PatrollingNPC(PATROL_SPRITESHEET),
                ),
                MapNPC(
                    starting=(2, 5),
                    npc=IdleNPC(IDLE_SPRITESHEET),
                ),
            ),
            impassable_ids={8, 7},
        )


# Entry point ---------------------------------------------------------------

def main() -> None:
    scene = SimpleMapScene()
    game = build_game(title="Simple RPG - Simple Map", initial_scene=scene, debug_collision=True)
    game.run()


if __name__ == "__main__":
    main()
