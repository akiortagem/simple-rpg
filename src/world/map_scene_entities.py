"""Stub entity builders for declarative map scenes.

Implement ``PC`` and ``NPC`` subclasses to customize how map declarations
produce runtime sprites and NPC route behaviors.
"""

from __future__ import annotations

from .npc_routes import Route
from .sprites import PCMapSprite
from .spritesheet_declarative import SpriteSheet


class PC:
    """Declarative PC builder that produces a playable sprite.

    Hitbox measurements are in pixels, matching sprite frame size and position.
    ``hitbox_size`` defines the collision box size, and ``hitbox_offset`` shifts
    the hitbox relative to the sprite's top-left corner.
    """

    spritesheet: SpriteSheet
    hitbox_size: tuple[float, float] | None = None
    hitbox_offset: tuple[float, float] = (0.0, 0.0)

    def __new__(cls, spritesheet: SpriteSheet) -> PCMapSprite:
        instance = super().__new__(cls)
        instance.spritesheet = spritesheet
        return instance.create_sprite()

    def create_sprite(self) -> PCMapSprite:
        """Create the playable sprite for this PC definition."""

        name = getattr(self, "name", self.__class__.__name__)
        speed = getattr(self, "speed", 120.0)
        hitbox_size = getattr(self, "hitbox_size", None)
        hitbox_offset = getattr(self, "hitbox_offset", (0.0, 0.0))
        return PCMapSprite(
            name=name,
            x=0.0,
            y=0.0,
            spritesheet=self.spritesheet.to_descriptor(),
            speed=speed,
            hitbox_size=hitbox_size,
            hitbox_offset=hitbox_offset,
        )


class NPC:
    """Base NPC definition for declarative map scenes.

    Hitbox measurements are in pixels, matching sprite frame size and position.
    ``hitbox_size`` defines the collision box size, and ``hitbox_offset`` shifts
    the hitbox relative to the sprite's top-left corner.
    """

    spritesheet: SpriteSheet
    hitbox_size: tuple[float, float] | None = None
    hitbox_offset: tuple[float, float] = (0.0, 0.0)

    def __init__(self, spritesheet: SpriteSheet) -> None:
        self.spritesheet = spritesheet

    def patrol(self) -> Route | None:
        """Return the patrol route for this NPC."""

        return None

    async def interact(self, player: PCMapSprite) -> None:
        """Respond asynchronously to the player triggering interaction."""

        return None
