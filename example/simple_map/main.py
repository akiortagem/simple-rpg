"""Simple 10x10 overworld example with a patrol and idle NPC.

Asset filenames expected by this example:
- assets/tileset.png
- assets/player.png
- assets/npc_patrol.png
- assets/npc_idle.png
"""

from __future__ import annotations

from pathlib import Path

from src.game.domain.map_scene_declarative import Map, MapNPC, MapPC, TileSheet
from src.game.domain.map_scene_entities import NPC, PC
from src.game.domain.npc_routes import LoopRoute, NPCRoute, Route
from src.game.domain.scenes import MapSceneBase
from src.game.domain.sprites import PCMapSprite
from src.game.domain.spritesheet_declarative import SpriteSheet, SpriteSheetAnimations
from src.game.domain.ui_kit import Dialog
from src.main import build_game

ASSETS_DIR = Path(__file__).parent / "assets"
TILE_SIZE = 32


SPRITE_ANIMATIONS = SpriteSheetAnimations(
    actions={
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
    },
)

PLAYER_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "player.png",
    frame_width=TILE_SIZE,
    frame_height=TILE_SIZE,
    columns=4,
    animations=SPRITE_ANIMATIONS,
)

PATROL_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "npc_patrol.png",
    frame_width=TILE_SIZE,
    frame_height=TILE_SIZE,
    columns=4,
    animations=SPRITE_ANIMATIONS,
)

IDLE_SPRITESHEET = SpriteSheet(
    image=ASSETS_DIR / "npc_idle.png",
    frame_width=TILE_SIZE,
    frame_height=TILE_SIZE,
    columns=4,
    animations=SPRITE_ANIMATIONS,
)


# World construction --------------------------------------------------------

MAP_SIZE = 10


class PlayerPC(PC):
    name = "Player"
    speed = 140.0


class PatrollingNPC(NPC):
    def __init__(self, spritesheet: SpriteSheet, *, start: tuple[float, float]) -> None:
        super().__init__(spritesheet)
        self._start = start

    def patrol(self) -> Route | None:
        span = 2 * TILE_SIZE
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
        Dialog("The patrol keeps marching along.")


class IdleNPC(NPC):
    def patrol(self) -> Route | None:
        return NPCRoute(waypoints=(), loop=True, wait_time=0.0)

    def interact(self, player: PCMapSprite) -> None:
        Dialog("The idle NPC smiles politely.")


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
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 3, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
        ]
        tile_sheet = TileSheet(
            image=ASSETS_DIR / "tileset.png",
            tile_width=TILE_SIZE,
            tile_height=TILE_SIZE,
            columns=4,
        )

        return Map(
            tile_sheet=tile_sheet,
            tiles=tiles,
            pc=MapPC(starting=(2 * TILE_SIZE, 2 * TILE_SIZE), pc=PlayerPC, sprite=PLAYER_SPRITESHEET),
            npcs=(
                MapNPC(
                    starting=(7 * TILE_SIZE, 2 * TILE_SIZE),
                    npc=PatrollingNPC,
                    sprite=PATROL_SPRITESHEET,
                ),
                MapNPC(
                    starting=(2 * TILE_SIZE, 7 * TILE_SIZE),
                    npc=IdleNPC,
                    sprite=IDLE_SPRITESHEET,
                ),
            ),
            impassable_ids={2, 3},
        )


# Entry point ---------------------------------------------------------------

def main() -> None:
    scene = SimpleMapScene()
    game = build_game(title="Simple RPG - Simple Map", initial_scene=scene)
    game.run()


if __name__ == "__main__":
    main()
