"""Sprite utilities for animating character entities.

The spritesheet layout is assumed to be a grid of equally sized frames arranged
row-by-row (left-to-right, then top-to-bottom). Frame indices count across rows
in row-major order, so index 0 references the top-left frame and increments to
the right before wrapping to the next row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .contracts import Renderer
from .entities import Entity

AnimationMap = Dict[str, Dict[str, List[int]]]


@dataclass(frozen=True)
class SpriteSheetDescriptor:
    """Metadata describing how to slice a spritesheet image.

    Attributes:
        image: Framework-specific image/surface object that the renderer
            understands (for example, a ``pygame.Surface``).
        frame_width: Width of a single frame in pixels.
        frame_height: Height of a single frame in pixels.
        columns: Optional number of columns in the spritesheet grid. Providing
            this avoids renderer-specific queries for surface dimensions and is
            required when the renderer cannot infer them.
        animations: Optional mapping of actions and directions to the frame
            indices that compose the animation. When omitted, the sprite will
            assume a single "idle" action and "down" direction that references
            the first frame (index 0).
    """

    image: object
    frame_width: int
    frame_height: int
    columns: int | None = None
    animations: AnimationMap | None = None


@dataclass
class CharacterSprite(Entity):
    """Animated character sprite that can render frames from a spritesheet."""

    spritesheet: SpriteSheetDescriptor
    frame_duration: float = 0.12
    current_action: str = "idle"
    current_direction: str = "down"
    _current_frame_index: int = field(default=0, init=False)
    _frame_elapsed: float = field(default=0.0, init=False)

    def determine_animation_state(self) -> tuple[str, str]:  # pragma: no cover - intended for subclass override
        """Hook for subclasses to choose the current animation state.

        Override this method to return a tuple of (action, direction) based on
        movement state, input, or other factors. The default implementation
        returns the existing ``current_action`` and ``current_direction``
        values.
        """

        return self.current_action, self.current_direction

    def set_animation_state(self, action: str, direction: str) -> None:
        """Update the animation state and reset the timeline when it changes."""

        if (action, direction) != (self.current_action, self.current_direction):
            self.current_action = action
            self.current_direction = direction
            self._current_frame_index = 0
            self._frame_elapsed = 0.0

    def update(self, delta_time: float) -> None:
        desired_action, desired_direction = self.determine_animation_state()
        self.set_animation_state(desired_action, desired_direction)

        frames = self._frames_for_state()
        if not frames:
            return

        self._frame_elapsed += delta_time
        while self._frame_elapsed >= self.frame_duration:
            self._frame_elapsed -= self.frame_duration
            self._current_frame_index = (self._current_frame_index + 1) % len(frames)

    def render(self, renderer: Renderer, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Draw the current frame at the entity's position using the renderer."""

        frames = self._frames_for_state()
        if not frames:
            return

        frame_index = frames[self._current_frame_index]
        source_rect = self._source_rect_for_frame(frame_index)
        destination = (int(self.x - camera_offset[0]), int(self.y - camera_offset[1]))
        renderer.draw_image(self.spritesheet.image, source_rect, destination)

    # Internal helpers -----------------------------------------------------
    def _frames_for_state(self) -> List[int]:
        animations = self.spritesheet.animations or {
            "idle": {"down": [0]},
        }
        return animations.get(self.current_action, {}).get(self.current_direction, [])

    def _source_rect_for_frame(self, frame_index: int) -> tuple[int, int, int, int]:
        columns = self.spritesheet.columns
        if columns is None:
            # Fallback to a single-row spritesheet when column count is unknown.
            columns = frame_index + 1
        row = frame_index // columns
        col = frame_index % columns
        return (
            col * self.spritesheet.frame_width,
            row * self.spritesheet.frame_height,
            self.spritesheet.frame_width,
            self.spritesheet.frame_height,
        )
