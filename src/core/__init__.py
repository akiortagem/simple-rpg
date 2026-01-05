"""Core engine-agnostic contracts and entities.

Import the foundational types for engine wiring from this module, including
``Renderer``/``EventSource``/``TimeSource`` protocols, ``InputEvent`` and
``GameConfig`` data, plus the ``Entity`` base class for lightweight domain
objects.
"""

from .contracts import Color, EventSource, GameConfig, InputEvent, Key, Renderer, TimeSource
from .entities import Entity

__all__ = [
    "Color",
    "Entity",
    "EventSource",
    "GameConfig",
    "InputEvent",
    "Key",
    "Renderer",
    "TimeSource",
]
