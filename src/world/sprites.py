"""Sprite utilities for animating character entities.

Use ``normalize_animation_map`` and ``SpriteSheetDescriptor`` to prepare
animations, then instantiate ``CharacterSprite`` or map-aware subclasses like
``PCMapSprite`` and ``NPCMapSprite`` for runtime rendering. The spritesheet
layout is assumed to be a grid of equally sized frames arranged row-by-row
(left-to-right, then top-to-bottom). Frame indices count across rows in
row-major order, so index 0 references the top-left frame and increments to the
right before wrapping to the next row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Protocol, Sequence, Set, Tuple

from ..core.contracts import Key, Renderer
from ..core.entities import Entity

AnimationMap = Dict[str, Dict[str, List[int]]]
DEFAULT_DIRECTION_ORDER = ("down", "left", "right", "up")


def normalize_animation_map(
    actions: Mapping[str, object],
    *,
    directions: Sequence[str] = DEFAULT_DIRECTION_ORDER,
    one_indexed: bool = False,
    sheet_size: tuple[int, int] | None = None,
) -> AnimationMap:
    """Normalize animation definitions into a frame index map.

    Args:
        actions: Mapping of action names to direction mappings or ordered
            direction lists. Direction lists are interpreted using
            ``directions`` ordering.
        directions: Direction order used when animations are declared as
            ordered lists.
        one_indexed: Whether the incoming frame IDs are 1-based.
        sheet_size: ``(columns, rows)`` in frames. Required when ``one_indexed``
            is ``True`` so validation can occur.
    """

    if one_indexed and sheet_size is None:
        raise ValueError("sheet_size is required when using 1-based tile IDs.")

    max_tile_id = None
    if sheet_size is not None:
        columns, rows = sheet_size
        if columns <= 0 or rows <= 0:
            raise ValueError("sheet_size must contain positive column/row counts.")
        max_tile_id = columns * rows

    normalized: AnimationMap = {}
    for action, raw_directions in actions.items():
        normalized[action] = _normalize_action(
            raw_directions,
            directions=directions,
            one_indexed=one_indexed,
            max_tile_id=max_tile_id,
            action=action,
        )
    return normalized


def _normalize_action(
    raw_directions: object,
    *,
    directions: Sequence[str],
    one_indexed: bool,
    max_tile_id: int | None,
    action: str,
) -> Dict[str, List[int]]:
    if isinstance(raw_directions, Mapping):
        return {
            direction: _normalize_frames(
                frames,
                one_indexed=one_indexed,
                max_tile_id=max_tile_id,
                action=action,
                direction=direction,
            )
            for direction, frames in raw_directions.items()
        }

    if _is_sequence(raw_directions):
        if _is_int_sequence(raw_directions):
            return _normalize_direction_list(
                raw_directions,
                directions=directions,
                one_indexed=one_indexed,
                max_tile_id=max_tile_id,
                action=action,
            )

        if _is_sequence_of_sequences(raw_directions):
            return _normalize_direction_frames_list(
                raw_directions,
                directions=directions,
                one_indexed=one_indexed,
                max_tile_id=max_tile_id,
                action=action,
            )

    raise TypeError(
        "Animations must be mappings of directions or ordered frame lists."
    )


def _normalize_direction_list(
    frames: Sequence[int],
    *,
    directions: Sequence[str],
    one_indexed: bool,
    max_tile_id: int | None,
    action: str,
) -> Dict[str, List[int]]:
    if len(frames) != len(directions):
        raise ValueError(
            f"Action '{action}' defines {len(frames)} directions, "
            f"expected {len(directions)}."
        )
    return {
        direction: _normalize_frames(
            [frame],
            one_indexed=one_indexed,
            max_tile_id=max_tile_id,
            action=action,
            direction=direction,
        )
        for direction, frame in zip(directions, frames)
    }


def _normalize_direction_frames_list(
    frames: Sequence[Sequence[int]],
    *,
    directions: Sequence[str],
    one_indexed: bool,
    max_tile_id: int | None,
    action: str,
) -> Dict[str, List[int]]:
    if len(frames) != len(directions):
        raise ValueError(
            f"Action '{action}' defines {len(frames)} directions, "
            f"expected {len(directions)}."
        )
    normalized: Dict[str, List[int]] = {}
    for direction, direction_frames in zip(directions, frames):
        if not _is_int_sequence(direction_frames):
            raise TypeError(
                "Direction animations must be sequences of integers."
            )
        normalized[direction] = _normalize_frames(
            direction_frames,
            one_indexed=one_indexed,
            max_tile_id=max_tile_id,
            action=action,
            direction=direction,
        )
    return normalized


def _normalize_frames(
    frames: object,
    *,
    one_indexed: bool,
    max_tile_id: int | None,
    action: str,
    direction: str,
) -> List[int]:
    if isinstance(frames, int):
        frame_list = [frames]
    elif _is_int_sequence(frames):
        frame_list = list(frames)
    else:
        raise TypeError("Animation frames must be integers or integer sequences.")

    normalized: List[int] = []
    for frame in frame_list:
        _validate_frame_id(frame, max_tile_id, one_indexed, action, direction)
        normalized.append(frame - 1 if one_indexed else frame)
    return normalized


def _validate_frame_id(
    frame_id: int,
    max_tile_id: int | None,
    one_indexed: bool,
    action: str,
    direction: str,
) -> None:
    if max_tile_id is None:
        return

    minimum = 1 if one_indexed else 0
    maximum = max_tile_id if one_indexed else max_tile_id - 1
    if frame_id < minimum or frame_id > maximum:
        raise ValueError(
            f"Animation frame {frame_id} for '{action}:{direction}' "
            f"must be between {minimum} and {maximum}."
        )


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _is_int_sequence(value: object) -> bool:
    return _is_sequence(value) and all(isinstance(item, int) for item in value)


def _is_sequence_of_sequences(value: object) -> bool:
    if not _is_sequence(value) or _is_int_sequence(value):
        return False
    return all(_is_sequence(item) for item in value)


@dataclass(frozen=True)
class SpriteSheetDescriptor:
    """Metadata describing how to slice a spritesheet image.

    Attributes:
        image: File path to the spritesheet image. Renderers are responsible
            for loading the image data from disk.
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

    image: str | Path
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

    @property
    def pixel_size(self) -> tuple[int, int]:
        """Total size of the collidable map in pixels."""
        ...

    def collides(self, hitbox: tuple[float, float, float, float]) -> bool:
        """Return ``True`` when the given hitbox overlaps blocked space."""
        ...


@dataclass(kw_only=True)
class CharacterMapSprite(CharacterSprite):
    """A character sprite aware of map bounds and collision layers.

    Hitbox measurements are in pixels (the same coordinate space as the sprite
    position and spritesheet frame size). ``hitbox_size`` defines the width and
    height of the collision box. ``hitbox_offset`` shifts the hitbox relative to
    the sprite's top-left corner.
    """

    hitbox_size: tuple[float, float] | None = None
    hitbox_offset: tuple[float, float] = (0.0, 0.0)
    speed: float = 120.0
    velocity: tuple[float, float] = (0.0, 0.0)
    map_bounds: tuple[int, int] | None = None
    collision_detector: CollisionDetector | None = None
    sprite_colliders: (
        Sequence[Callable[[], tuple[float, float, float, float]]]
        | Callable[[], Sequence[tuple[float, float, float, float]]]
        | None
    ) = None
    _facing_direction: str = field(default="down", init=False)
    _blocked: bool = field(default=False, init=False)

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

        self._blocked = False
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
            self._blocked = True
            return self.x if axis == "x" else self.y
        return clamped

    def _clamp_to_bounds(self, proposed: float, size: float, axis: str) -> float:
        if not self.map_bounds:
            return proposed
        limit = self.map_bounds[0] if axis == "x" else self.map_bounds[1]
        return max(0.0, min(proposed, max(limit - size, 0.0)))

    def _collides(self, hitbox: tuple[float, float, float, float]) -> bool:
        if self.collision_detector and self.collision_detector.collides(hitbox):
            return True
        for collider_hitbox in self._sprite_hitboxes():
            if collider_hitbox == self.hitbox:
                continue
            if _intersects(hitbox, collider_hitbox):
                return True
        return False

    def _hitbox(self, x: float, y: float) -> tuple[float, float, float, float]:
        frame_width = float(self.spritesheet.frame_width)
        frame_height = float(self.spritesheet.frame_height)
        if self.hitbox_size is None:
            width = frame_width * 0.75
            height = frame_height * 0.75
            if self.hitbox_offset == (0.0, 0.0):
                offset_x = (frame_width - width) / 2
                offset_y = (frame_height - height) / 2
            else:
                offset_x, offset_y = self.hitbox_offset
        else:
            width, height = self.hitbox_size
            offset_x, offset_y = self.hitbox_offset
        return (x + offset_x, y + offset_y, width, height)

    def hitbox_at(self, x: float, y: float) -> tuple[float, float, float, float]:
        """Hitbox for the character sprite anchored at the given position."""

        return self._hitbox(x, y)

    def collides_with(self, hitbox: tuple[float, float, float, float]) -> bool:
        """Return whether the given hitbox collides with map or sprite blockers."""

        return self._collides(hitbox)

    def _sprite_hitboxes(self) -> Sequence[tuple[float, float, float, float]]:
        if self.sprite_colliders is None:
            return []
        if callable(self.sprite_colliders):
            return list(self.sprite_colliders())
        return [collider() for collider in self.sprite_colliders]

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

    @property
    def render_order_y(self) -> float:
        """Sort key for rendering order based on sprite's on-screen feet."""

        return self.y + float(self.spritesheet.frame_height)

    @property
    def blocked(self) -> bool:
        """Whether the last movement attempt was blocked by a collision."""

        return self._blocked


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


def _intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)
