"""Stub entity builders for declarative map scenes."""

from __future__ import annotations

from .spritesheet_declarative import SpriteSheet


class PC:
    """Placeholder PC builder type for declarative maps."""

    def __init__(self, sprite: SpriteSheet) -> None:
        pass


class NPC:
    """Placeholder NPC builder type for declarative maps."""

    def __init__(self, sprite: SpriteSheet) -> None:
        pass
