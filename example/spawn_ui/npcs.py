from __future__ import annotations

from dataclasses import dataclass

from src.scenes.utils import spawn_ui
from src.world.map_scene_entities import NPC, PC
from src.world.npc_routes import NPCRoute, Route
from src.world.sprites import PCMapSprite
from src.main import build_game

from .dialog_ui import DialogUI

@dataclass(frozen=True)
class PatrolRoute(Route):
    span: float
    wait_time: float = 0.6

    def resolve(self, start: tuple[float, float]) -> NPCRoute:
        start_x, start_y = start
        span = self.span
        return NPCRoute(
            waypoints=(
                (start_x, start_y),
                (start_x + span, start_y),
                (start_x + span, start_y + span),
                (start_x, start_y + span),
            ),
            loop=True,
            wait_time=self.wait_time,
        )


class PatrollingNPC(NPC):
    hitbox_size = HITBOX_SIZE
    hitbox_offset = HITBOX_OFFSET

    def patrol(self) -> Route | None:
        return PatrolRoute(span=1 * TILE_SIZE)

    async def interact(self, player: PCMapSprite) -> None: # when interacting with NPCs, the interacting NPC should be frozen if they have route, and the PC should ignore any keypresses
        await spawn_ui(DialogUI("How long should I walk? I'm getting tired. . .")) # spawn_ui will by default run in async, but caller can use await so that they wait for the UI to despawn before executing next statements


class IdleNPC(NPC):
    hitbox_size = HITBOX_SIZE
    hitbox_offset = HITBOX_OFFSET

    def patrol(self) -> Route | None:
        return NPCRoute(waypoints=(), loop=True, wait_time=0.0)

    async def interact(self, player: PCMapSprite) -> None:
        await spawn_ui(DialogUI("I think  that sweetrolls are swell!")) # spawn_ui will by default run in async, but caller can use await so that they wait for the UI to despawn before executing next statements