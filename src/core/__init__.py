"""Core engine-agnostic contracts and entities."""

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
