"""Sprite utilities for animating character entities.

The spritesheet layout is assumed to be a grid of equally sized frames arranged
row-by-row (left-to-right, then top-to-bottom). Frame indices count across rows
in row-major order, so index 0 references the top-left frame and increments to
the right before wrapping to the next row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Protocol, Set, Tuple

from .contracts import Key, Renderer
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


@dataclass(kw_only=True)
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


class CollisionDetector(Protocol):
    """Strategy for querying whether a hitbox intersects impassable terrain."""

    def collides(self, hitbox: tuple[float, float, float, float]) -> bool:
        """Return ``True`` when the given hitbox overlaps blocked space."""
        ...


@dataclass(kw_only=True)
class CharacterMapSprite(CharacterSprite):
    """A character sprite aware of map bounds and collision layers."""

    speed: float = 120.0
    velocity: tuple[float, float] = (0.0, 0.0)
    map_bounds: tuple[int, int] | None = None
    collision_detector: CollisionDetector | None = None
    _facing_direction: str = field(default="down", init=False)

    def determine_animation_state(self) -> tuple[str, str]:
        if self.velocity != (0.0, 0.0):
            direction = self._direction_from_vector(*self.velocity)
            self._facing_direction = direction
            return "walk", direction
        return "idle", self._facing_direction

    def update(self, delta_time: float) -> None:
        self._integrate_velocity(delta_time)
        super().update(delta_time)

    # Movement helpers ----------------------------------------------------
    def _integrate_velocity(self, delta_time: float) -> None:
        if delta_time <= 0 or self.velocity == (0.0, 0.0):
            return

        target_x = self.x + self.velocity[0] * delta_time
        target_y = self.y + self.velocity[1] * delta_time

        self.x = self._resolve_axis_move(target_x, self.y, axis="x")
        self.y = self._resolve_axis_move(target_y, self.x, axis="y")

    def _resolve_axis_move(self, proposed_primary: float, secondary: float, axis: str) -> float:
        width = self.spritesheet.frame_width
        height = self.spritesheet.frame_height
        primary_size = width if axis == "x" else height

        clamped = self._clamp_to_bounds(proposed_primary, primary_size, axis)
        hitbox = self._hitbox(clamped if axis == "x" else self.x, secondary if axis == "x" else clamped)
        if self._collides(hitbox):
            return self.x if axis == "x" else self.y
        return clamped

    def _clamp_to_bounds(self, proposed: float, size: float, axis: str) -> float:
        if not self.map_bounds:
            return proposed
        limit = self.map_bounds[0] if axis == "x" else self.map_bounds[1]
        return max(0.0, min(proposed, max(limit - size, 0.0)))

    def _collides(self, hitbox: tuple[float, float, float, float]) -> bool:
        if self.collision_detector is None:
            return False
        return self.collision_detector.collides(hitbox)

    def _hitbox(self, x: float, y: float) -> tuple[float, float, float, float]:
        return (
            x,
            y,
            float(self.spritesheet.frame_width),
            float(self.spritesheet.frame_height),
        )

    def _direction_from_vector(self, dx: float, dy: float) -> str:
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        if abs(dy) > 0:
            return "down" if dy > 0 else "up"
        return self._facing_direction

    @property
    def facing_direction(self) -> str:
        """Direction the character is currently facing."""

        return self._facing_direction

    @property
    def hitbox(self) -> tuple[float, float, float, float]:
        """Current hitbox of the character sprite."""

        return self._hitbox(self.x, self.y)


class PCMapSprite(CharacterMapSprite):
    """Playable character that responds to input."""

    def handle_input(self, pressed: Set[str]) -> None:
        """Update velocity and facing based on the provided input set."""

        dx = 0.0
        dy = 0.0
        if Key.LEFT in pressed:
            dx -= 1
        if Key.RIGHT in pressed:
            dx += 1
        if Key.UP in pressed:
            dy -= 1
        if Key.DOWN in pressed:
            dy += 1

        if dx or dy:
            magnitude = (dx * dx + dy * dy) ** 0.5
            dx /= magnitude
            dy /= magnitude
            self.velocity = (dx * self.speed, dy * self.speed)
            self._facing_direction = self._direction_from_vector(dx, dy)
        else:
            self.velocity = (0.0, 0.0)


class NPCMapSprite(CharacterMapSprite):
    """Non-player character sprite that ignores direct input."""

    def handle_input(self, pressed: Set[str]) -> None:  # pragma: no cover - NPCs ignore input
        return None
