"""Stub entity builders for declarative map scenes."""

from __future__ import annotations

from .npc_routes import Route
from .sprites import PCMapSprite
from .spritesheet_declarative import SpriteSheet


class PC:
    """Declarative PC builder that produces a playable sprite."""

    spritesheet: SpriteSheet

    def __new__(cls, spritesheet: SpriteSheet) -> PCMapSprite:
        instance = super().__new__(cls)
        instance.spritesheet = spritesheet
        return instance.create_sprite()

    def create_sprite(self) -> PCMapSprite:
        """Create the playable sprite for this PC definition."""

        name = getattr(self, "name", self.__class__.__name__)
        speed = getattr(self, "speed", 120.0)
        return PCMapSprite(
            name=name,
            x=0.0,
            y=0.0,
            spritesheet=self.spritesheet.to_descriptor(),
            speed=speed,
        )


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
