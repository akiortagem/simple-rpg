"""Renderable tilemap layer implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ..core.contracts import Renderer


@dataclass(frozen=True)
class TilesetDescriptor:
    """Metadata describing how to slice a tilemap image.

    ``image`` should be a file path that the renderer can load.
    """

    image: str | Path
    tile_width: int
    tile_height: int
    columns: int


class TilemapLayer:
    """Renderable tilemap layer backed by a grid of tile identifiers."""

    def __init__(
        self,
        tileset: TilesetDescriptor,
        tiles: Sequence[Sequence[int | None]],
        tile_offsets: Sequence[Sequence[tuple[int, int] | None]] | None = None,
    ) -> None:
        self.tileset = tileset
        self.tiles = tiles
        self.tile_offsets = tile_offsets

        self.tile_size = (tileset.tile_width, tileset.tile_height)
        rows = len(tiles)
        columns = len(tiles[0]) if rows else 0
        self.pixel_size = (columns * tileset.tile_width, rows * tileset.tile_height)

    def render(self, renderer: Renderer, camera_offset: tuple[int, int] = (0, 0)) -> None:
        tile_width, tile_height = self.tile_size
        if tile_width <= 0 or tile_height <= 0:
            return

        view_width, view_height = renderer.size
        camera_x, camera_y = camera_offset

        rows = len(self.tiles)
        columns = len(self.tiles[0]) if rows else 0
        if rows == 0 or columns == 0:
            return

        start_column = max(0, int(camera_x // tile_width))
        end_column = min(columns, int((camera_x + view_width + tile_width - 1) // tile_width))
        start_row = max(0, int(camera_y // tile_height))
        end_row = min(rows, int((camera_y + view_height + tile_height - 1) // tile_height))

        for row in range(start_row, end_row):
            tile_row = self.tiles[row]
            offset_row = self.tile_offsets[row] if self.tile_offsets and row < len(self.tile_offsets) else None
            for column in range(start_column, end_column):
                tile_id = tile_row[column]
                if tile_id is None or tile_id < 0:
                    continue

                source_rect = self._source_rect(tile_id)
                offset = (0, 0)
                if offset_row and column < len(offset_row) and offset_row[column]:
                    offset = offset_row[column]  # type: ignore[assignment]

                destination = (
                    int(column * tile_width - camera_x + offset[0]),
                    int(row * tile_height - camera_y + offset[1]),
                )
                renderer.draw_image(self.tileset.image, source_rect, destination)

    def _source_rect(self, tile_id: int) -> tuple[int, int, int, int]:
        columns = self.tileset.columns
        row = tile_id // columns
        column = tile_id % columns
        return (
            column * self.tileset.tile_width,
            row * self.tileset.tile_height,
            self.tileset.tile_width,
            self.tileset.tile_height,
        )
