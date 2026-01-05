"""Declarative spritesheet definitions for map scenes.

Define ``SpriteSheet`` and ``SpriteSheetAnimations`` to describe animation
frames without touching rendering code, then feed them into map declarations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .sprites import SpriteSheetDescriptor, normalize_animation_map


@dataclass(frozen=True)
class SpriteSheetAnimations:
    """Declarative animation definitions for a spritesheet.

    The frame indices are integers that refer to frames in the spritesheet grid,
    counted left-to-right then top-to-bottom (row-major order), matching
    ``SpriteSheetDescriptor`` expectations.

    Animations can be expressed as either explicit direction mappings or as
    ordered lists using the direction order (down, left, right, up). For example
    ``idle=[2, 5, 8, 11]`` becomes ``{"down": [2], "left": [5], ...}`` and
    ``walk=[[1, 2, 3], ...]`` becomes ``{"down": [1, 2, 3], ...}``.
    """

    actions: Mapping[str, object]

    def to_animation_map(
        self,
        *,
        sheet_size: tuple[int, int] | None = None,
        one_indexed: bool = False,
    ) -> dict[str, dict[str, list[int]]]:
        return normalize_animation_map(
            self.actions,
            sheet_size=sheet_size,
            one_indexed=one_indexed,
        )


@dataclass(frozen=True)
class SpriteSheet:
    """Declarative spritesheet descriptor.

    ``frame_width``/``frame_height`` describe the size (in pixels) of each frame.
    ``columns`` indicates how many frames appear in each row of the sheet; frame
    indices in ``SpriteSheetAnimations`` use this value to locate a frame in the
    grid.
    """

    image: str | Path
    frame_width: int
    frame_height: int
    columns: int | None = None
    animations: SpriteSheetAnimations | None = None

    def to_descriptor(self) -> SpriteSheetDescriptor:
        return SpriteSheetDescriptor(
            image=self.image,
            frame_width=self.frame_width,
            frame_height=self.frame_height,
            columns=self.columns,
            animations=self.animations.to_animation_map() if self.animations else None,
        )
