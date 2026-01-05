"""Domain entities for the Simple RPG.

These classes purposefully avoid framework-specific details so they can be reused
across different presentation technologies. Subclass ``Entity`` for simple
positioned objects and override ``Entity.update`` to participate in the game
loop without binding to a specific renderer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entity:
    """A lightweight entity with positional data."""

    name: str
    x: float = 0
    y: float = 0

    def update(self, delta_time: float) -> None:  # pragma: no cover - stub logic
        """Update the entity. Override to implement behavior."""
        return None
