"""Helpers for parsing tilemap text assets.

Use ``parse_tilemap`` to turn text-based tilemap definitions into 2D integer
grids suitable for ``Tilemap`` and ``TilemapLayer`` initialization.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable


_TOKEN_SPLIT = re.compile(r"[\s,]+")


def parse_tilemap(
    *,
    tilemap: str | None = None,
    tilemap_file: str | Path | None = None,
    collision: bool = False,
) -> list[list[int]]:
    """Parse tilemap data from a multiline string or file.

    Args:
        tilemap: Multiline string containing tile IDs.
        tilemap_file: File path containing tile IDs.
        collision: When ``True``, do not convert 1-based tile IDs.

    Returns:
        A 2D list of integers representing tile IDs.
    """

    if (tilemap is None) == (tilemap_file is None):
        raise ValueError("Provide exactly one of tilemap or tilemap_file.")

    if tilemap_file is not None:
        tilemap = Path(tilemap_file).read_text(encoding="utf-8")

    if tilemap is None:
        return []

    rows = _parse_rows(tilemap)
    if not rows:
        return []

    columns = len(rows[0])
    for row_index, row in enumerate(rows):
        if len(row) != columns:
            raise ValueError(
                f"Row {row_index} has {len(row)} columns; expected {columns}."
            )

    if collision:
        return rows

    return [[value - 1 if value > 0 else -1 for value in row] for row in rows]


def _parse_rows(tilemap: str) -> list[list[int]]:
    lines = [line.strip() for line in tilemap.splitlines() if line.strip()]
    return [_parse_line(line) for line in lines]


def _parse_line(line: str) -> list[int]:
    tokens: Iterable[str] = (token for token in _TOKEN_SPLIT.split(line) if token)
    return [int(token) for token in tokens]
