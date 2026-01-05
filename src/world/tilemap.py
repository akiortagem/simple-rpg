"""Tilemap utilities for rendering and collision queries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .sprites import CollisionDetector


@dataclass
class Tilemap:
    """A simple 2D grid of tile identifiers.

    Attributes:
        tiles: Rows of tile IDs arranged in row-major order.
        tile_size: Tuple of ``(width, height)`` in pixels for each tile.
        impassable_ids: Set of tile IDs that block movement.
    """

    tiles: Sequence[Sequence[int]]
    tile_size: tuple[int, int]
    impassable_ids: set[int] = field(default_factory=set)

    @property
    def rows(self) -> int:
        return len(self.tiles)

    @property
    def columns(self) -> int:
        return len(self.tiles[0]) if self.tiles else 0

    @property
    def pixel_size(self) -> tuple[int, int]:
        width, height = self.tile_size
        return (self.columns * width, self.rows * height)

    def tile_at(self, row: int, column: int) -> int | None:
        if row < 0 or column < 0 or row >= self.rows or column >= self.columns:
            return None
        return self.tiles[row][column]

    def is_impassable(self, row: int, column: int) -> bool:
        tile = self.tile_at(row, column)
        if tile is None:
            return True
        return tile in self.impassable_ids


@dataclass
class TileCollisionDetector(CollisionDetector):
    """Collision detector that maps hitboxes to impassable tiles."""

    tilemap: Tilemap

    @property
    def pixel_size(self) -> tuple[int, int]:
        return self.tilemap.pixel_size

    def collides(self, hitbox: tuple[float, float, float, float]) -> bool:
        x, y, width, height = hitbox
        tile_width, tile_height = self.tilemap.tile_size

        if width <= 0 or height <= 0:
            return False

        min_column = int(x // tile_width)
        max_column = int((x + width - 1) // tile_width)
        min_row = int(y // tile_height)
        max_row = int((y + height - 1) // tile_height)

        for row in range(min_row, max_row + 1):
            for column in range(min_column, max_column + 1):
                if self.tilemap.is_impassable(row, column):
                    return True
        return False
