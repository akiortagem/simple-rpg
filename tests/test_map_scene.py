import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.game.domain.contracts import InputEvent, Key
from src.game.domain.scenes import MapScene
from src.game.domain.sprites import CharacterMapSprite, SpriteSheetDescriptor


class FakeRenderer:
    def __init__(self):
        self.size = (320, 240)
        self.clears = []
        self.draw_images = []

    def clear(self, color):
        self.clears.append(color)

    def draw_rect(self, color, rect):
        return None

    def draw_image(self, image, source_rect, destination):
        self.draw_images.append((image, source_rect, destination))

    def draw_text(self, text, position, color, font_size=32, center=False):
        return None

    def present(self):
        return None


class FakeTilemap:
    def __init__(self):
        self.pixel_size = (100, 100)
        self.render_calls = []
        self.blocked = False
        self.hitboxes = []

    def render(self, renderer, camera_offset=(0, 0)):
        self.render_calls.append((renderer, camera_offset))

    def collides(self, hitbox):
        self.hitboxes.append(hitbox)
        return self.blocked


class FakeManager:
    def __init__(self, active_sprite=None, camera_offset=(0, 0)):
        self.active_sprite = active_sprite
        self.camera_offset = camera_offset
        self.update_calls = []
        self.render_calls = []

    def update(self, delta_time, sprites):
        self.update_calls.append((delta_time, list(sprites)))

    def render(self, renderer):
        self.render_calls.append(renderer)


class InputCapturingSprite(CharacterMapSprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_input = None

    def handle_input(self, pressed):
        self.last_input = set(pressed)
        super().handle_input(pressed)


class UpdateTrackingSprite(CharacterMapSprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_calls = []

    def update(self, delta_time: float) -> None:
        self.update_calls.append(delta_time)
        super().update(delta_time)


def make_sprite(cls=CharacterMapSprite, **kwargs):
    descriptor = SpriteSheetDescriptor(
        image="image",
        frame_width=10,
        frame_height=10,
        columns=1,
        animations={"idle": {"down": [0]}, "walk": {"right": [0]}},
    )
    return cls(name=kwargs.pop("name", "hero"), spritesheet=descriptor, **kwargs)


def test_initializes_collision_and_bounds():
    tilemap = FakeTilemap()
    sprite = make_sprite()
    manager = FakeManager(active_sprite=sprite)

    scene = MapScene(tilemap, tilemap, [sprite], manager)

    assert sprite.collision_detector is tilemap
    assert sprite.map_bounds == tilemap.pixel_size
    assert not scene.should_exit()


def test_handle_events_routes_to_active_character():
    tilemap = FakeTilemap()
    active = make_sprite(InputCapturingSprite, name="active")
    inactive = make_sprite(InputCapturingSprite, name="inactive")
    manager = FakeManager(active_sprite=active)
    scene = MapScene(tilemap, tilemap, [inactive, active], manager)

    events = [
        InputEvent(type="KEYDOWN", payload={"key": Key.RIGHT}),
        InputEvent(type="KEYUP", payload={"key": Key.RIGHT}),
    ]

    scene.handle_events(events)

    assert active.last_input == set()
    assert inactive.last_input is None


def test_update_advances_sprites_and_manager():
    tilemap = FakeTilemap()
    sprite = make_sprite(UpdateTrackingSprite)
    manager = FakeManager(active_sprite=sprite)
    scene = MapScene(tilemap, tilemap, [sprite], manager)

    scene.update(0.5)

    assert sprite.update_calls == [0.5]
    assert manager.update_calls == [(0.5, [sprite])]


def test_collision_blocks_movement_when_detector_reports_hit():
    tilemap = FakeTilemap()
    tilemap.blocked = True
    sprite = make_sprite(InputCapturingSprite)
    manager = FakeManager(active_sprite=sprite)
    scene = MapScene(tilemap, tilemap, [sprite], manager)

    scene.handle_events([InputEvent(type="KEYDOWN", payload={"key": Key.RIGHT})])
    scene.update(1.0)

    assert sprite.x == 0
    assert sprite.y == 0
    assert tilemap.hitboxes, "Collision detector should be queried"


def test_render_draws_tilemap_sprites_and_overlays():
    tilemap = FakeTilemap()
    sprite = make_sprite()
    sprite.x = 10
    sprite.y = 20
    manager = FakeManager(active_sprite=sprite, camera_offset=(3, 4))
    renderer = FakeRenderer()
    scene = MapScene(tilemap, tilemap, [sprite], manager)

    scene.render(renderer)

    assert renderer.clears[-1] == scene.background_color
    assert tilemap.render_calls == [(renderer, manager.camera_offset)]
    assert renderer.draw_images[-1][2] == (7, 16)
    assert manager.render_calls == [renderer]
