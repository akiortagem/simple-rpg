"""Stub entity builders for declarative map scenes."""

from __future__ import annotations

from .npc_routes import Route
from .sprites import PCMapSprite
from .spritesheet_declarative import SpriteSheet


class PC:
    """Placeholder PC builder type for declarative maps."""

    def __init__(self, sprite: SpriteSheet) -> None:
        pass


class NPC:
    """Base NPC definition for declarative map scenes."""

    spritesheet: SpriteSheet

    def __init__(self, spritesheet: SpriteSheet) -> None:
        self.spritesheet = spritesheet

    def patrol(self) -> Route | None:
        """Return the patrol route for this NPC."""

        return None

    def interact(self, player: PCMapSprite) -> None:
        """Respond to the player triggering interaction."""

        return None
