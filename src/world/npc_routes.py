"""NPC patrol route helpers.

Use ``NPCRoute`` and ``Route`` definitions (like ``LoopRoute``) to describe how
NPCs should traverse waypoints within map scenes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence


class Route(Protocol):
    """Defines how an NPC patrol route is resolved from a starting position."""

    def resolve(self, start: tuple[float, float]) -> "NPCRoute":
        """Return the concrete route to traverse from the starting position."""


@dataclass(frozen=True)
class NPCRoute(Route):
    """Declarative route description for an NPC controller."""

    waypoints: Sequence[tuple[float, float]] = field(default_factory=tuple)
    """Positions the NPC should traverse in order."""

    loop: bool = True
    """Whether the NPC should restart at the first waypoint after finishing."""

    wait_time: float = 0.0
    """Optional pause applied after reaching each waypoint (in seconds)."""

    def resolve(self, start: tuple[float, float]) -> "NPCRoute":
        return self


@dataclass(frozen=True)
class LoopRoute(Route):
    """Route that traverses waypoints forward and then back."""

    waypoints: Sequence[tuple[float, float]] = field(default_factory=tuple)
    wait_time: float = 0.0

    def resolve(self, start: tuple[float, float]) -> NPCRoute:
        if not self.waypoints:
            return NPCRoute(waypoints=tuple(), loop=True, wait_time=self.wait_time)

        forward = list(self.waypoints)
        reverse_segment = list(reversed(forward[:-1]))
        looped = forward + reverse_segment
        return NPCRoute(waypoints=tuple(looped), loop=True, wait_time=self.wait_time)
