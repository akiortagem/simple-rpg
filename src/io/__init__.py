"""Infrastructure adapters and IO helpers.

This package provides concrete adapters like ``PygameRenderer`` and helper
functions such as ``load_image`` and ``parse_tilemap`` for asset loading and
tilemap parsing.
"""

from .assets import load_image
from .pygame_adapter import PygameClock, PygameEventSource, PygameRenderer
from .tilemap_parser import parse_tilemap

__all__ = [
    "PygameClock",
    "PygameEventSource",
    "PygameRenderer",
    "load_image",
    "parse_tilemap",
]
