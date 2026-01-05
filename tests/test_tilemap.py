import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.world.tilemap import TileCollisionDetector, Tilemap


def test_tilemap_reports_pixel_size_and_impassable_cells():
    tilemap = Tilemap(tiles=[[0, 1], [2, 0]], tile_size=(8, 16), impassable_ids={1})

    assert tilemap.pixel_size == (16, 32)
    assert tilemap.is_impassable(0, 1)
    assert not tilemap.is_impassable(1, 0)
    assert tilemap.is_impassable(-1, 0)
    assert tilemap.is_impassable(5, 5)


def test_collision_detector_checks_overlapping_cells():
    tilemap = Tilemap(tiles=[[0, 1], [2, 0]], tile_size=(10, 10), impassable_ids={1, 2})
    detector = TileCollisionDetector(tilemap)

    assert detector.pixel_size == (20, 20)
    assert detector.collides((9, 0, 2, 10))  # touches impassable tile (0, 1)
    assert detector.collides((0, 10, 10, 10))  # overlaps tile id 2
    assert not detector.collides((10, 10, 10, 10))
    assert detector.collides((-5, -5, 2, 2))  # outside map treated as blocked
