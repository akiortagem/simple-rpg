"""Controllers for NPC behavior within a map scene."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .map_scene_entities import NPC
from .npc_routes import NPCRoute, Route
from .sprites import NPCMapSprite, PCMapSprite


class NPCMapController(Protocol):
    """Protocol defining how NPCs are driven inside a map scene."""

    npc: NPCMapSprite | None

    def on_enter(self) -> None:
        """Hook invoked when the map scene becomes active."""

    def on_exit(self) -> None:
        """Hook invoked when the map scene is left."""

    def update(self, delta_time: float, player: PCMapSprite) -> None:
        """Advance controller state for the frame."""

    def interact(self, player: PCMapSprite) -> None:
        """Respond to the player triggering an interaction."""


@dataclass
class NPCController:
    """Controller that moves an NPC along a predefined route."""

    actor: NPC
    route: Route | None = None
    speed: float = 40.0
    default_span: float = 20.0
    interactions: int = field(default=0, init=False)
    npc: NPCMapSprite | None = field(default=None, init=False)
    _current_index: int = field(default=0, init=False)
    _elapsed: float = field(default=0.0, init=False)
    _waiting: bool = field(default=False, init=False)
    _active_route: NPCRoute | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        spritesheet = self.actor.spritesheet.to_descriptor()
        self.npc = NPCMapSprite(x=0.0, y=0.0, spritesheet=spritesheet, speed=self.speed)

    def on_enter(self) -> None:
        self._current_index = 0
        self._elapsed = 0.0
        self._waiting = False
        self.interactions = 0
        self._active_route = self._resolve_route()

    def on_exit(self) -> None:
        return None

    def update(self, delta_time: float, player: PCMapSprite) -> None:
        if self.npc is None or delta_time <= 0:
            return

        if self._active_route is None:
            return

        if not self._active_route.waypoints:
            self.npc.velocity = (0.0, 0.0)
            return

        if self._waiting:
            self._elapsed += delta_time
            self.npc.velocity = (0.0, 0.0)
            if self._elapsed < self._active_route.wait_time:
                return
            self._waiting = False
            self._elapsed = 0.0

        target_x, target_y = self._active_route.waypoints[self._current_index]
        dx = target_x - self.npc.x
        dy = target_y - self.npc.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance == 0:
            self._begin_wait_and_advance()
            self.npc.velocity = (0.0, 0.0)
            return

        step = self.speed * delta_time
        if distance <= step:
            self.npc.x = target_x
            self.npc.y = target_y
            self._begin_wait_and_advance()
            self.npc.velocity = (0.0, 0.0)
            return

        dx /= distance
        dy /= distance
        self.npc.velocity = (dx * self.speed, dy * self.speed)

    def interact(self, player: PCMapSprite) -> None:
        self.actor.interact(player)
        self.interactions += 1

    def _begin_wait_and_advance(self) -> None:
        assert self._active_route is not None

        self._waiting = self._active_route.wait_time > 0
        self._elapsed = 0.0
        if len(self._active_route.waypoints) == 0:
            return
        if self._current_index >= len(self._active_route.waypoints) - 1:
            if self._active_route.loop:
                self._current_index = 0
        else:
            self._current_index += 1

    def _resolve_route(self) -> NPCRoute | None:
        if self.npc is None:
            return None

        route = self.route or self.actor.patrol()
        if route is None:
            left = (self.npc.x - self.default_span, self.npc.y)
            right = (self.npc.x + self.default_span, self.npc.y)
            return NPCRoute(waypoints=(left, right), loop=True, wait_time=0.0)

        return route.resolve((self.npc.x, self.npc.y))
