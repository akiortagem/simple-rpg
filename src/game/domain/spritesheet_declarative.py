"""Declarative spritesheet definitions for map scenes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .sprites import SpriteSheetDescriptor


@dataclass(frozen=True)
class SpriteSheetAnimations:
    """Declarative animation definitions for a spritesheet.

    The frame indices are integers that refer to frames in the spritesheet grid,
    counted left-to-right then top-to-bottom (row-major order), matching
    ``SpriteSheetDescriptor`` expectations.
    """

    actions: Mapping[str, Mapping[str, Sequence[int]]]

    def to_animation_map(self) -> dict[str, dict[str, list[int]]]:
        return {
            action: {
                direction: list(frames) for direction, frames in directions.items()
            }
            for action, directions in self.actions.items()
        }


@dataclass(frozen=True)
class SpriteSheet:
    """Declarative spritesheet descriptor.

    ``frame_width``/``frame_height`` describe the size (in pixels) of each frame.
    ``columns`` indicates how many frames appear in each row of the sheet; frame
    indices in ``SpriteSheetAnimations`` use this value to locate a frame in the
    grid.
    """

    image: object
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
