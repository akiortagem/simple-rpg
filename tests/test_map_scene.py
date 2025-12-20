import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.game.domain.contracts import InputEvent, Key
from src.game.domain.npc_controller import NPCMapController
from src.game.domain.scenes import MapScene
from src.game.domain.sprites import NPCMapSprite, PCMapSprite, SpriteSheetDescriptor


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
    def __init__(self, pixel_size=(100, 100)):
        self.pixel_size = pixel_size
        self.render_calls = []
        self.blocked = False
        self.hitboxes = []

    def render(self, renderer, camera_offset=(0, 0)):
        self.render_calls.append((renderer, camera_offset))

    def collides(self, hitbox):
        self.hitboxes.append(hitbox)
        return self.blocked


class FakeController(NPCMapController):
    def __init__(self, npc=None):
        self.npc = npc
        self.update_calls = []
        self.interactions = []
        self.enter_calls = 0
        self.exit_calls = 0

    def on_enter(self):
        self.enter_calls += 1

    def on_exit(self):
        self.exit_calls += 1

    def update(self, delta_time, player):
        self.update_calls.append((delta_time, player))

    def interact(self, player):
        self.interactions.append(player)


class InputCapturingSprite(PCMapSprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_input = None

    def handle_input(self, pressed):
        self.last_input = set(pressed)
        super().handle_input(pressed)


class UpdateTrackingSprite(PCMapSprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_calls = []

    def update(self, delta_time: float) -> None:
        self.update_calls.append(delta_time)
        super().update(delta_time)


def make_sprite(cls=PCMapSprite, **kwargs):
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
    player = make_sprite()
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    controller = FakeController(npc=npc)

    scene = MapScene(tilemap, tilemap, player, [controller])

    assert player.collision_detector is tilemap
    assert npc.collision_detector is tilemap
    assert player.map_bounds == tilemap.pixel_size
    assert not scene.should_exit()


def test_handle_events_routes_to_active_character():
    tilemap = FakeTilemap()
    player = make_sprite(InputCapturingSprite, name="player")
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    controller = FakeController(npc=npc)
    scene = MapScene(tilemap, tilemap, player, [controller])

    events = [
        InputEvent(type="KEYDOWN", payload={"key": Key.RIGHT}),
        InputEvent(type="KEYUP", payload={"key": Key.RIGHT}),
    ]

    scene.handle_events(events)

    assert player.last_input == set()


def test_update_advances_sprites_and_manager():
    tilemap = FakeTilemap()
    player = make_sprite(UpdateTrackingSprite)
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    controller = FakeController(npc=npc)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.update(0.5)

    assert player.update_calls == [0.5]
    assert controller.update_calls == [(0.5, player)]


def test_collision_blocks_movement_when_detector_reports_hit():
    tilemap = FakeTilemap()
    tilemap.blocked = True
    player = make_sprite(InputCapturingSprite)
    scene = MapScene(tilemap, tilemap, player)

    scene.handle_events([InputEvent(type="KEYDOWN", payload={"key": Key.RIGHT})])
    scene.update(1.0)

    assert player.x == 0
    assert player.y == 0
    assert tilemap.hitboxes, "Collision detector should be queried"


def test_render_draws_tilemap_sprites_and_overlays():
    tilemap = FakeTilemap()
    player = make_sprite()
    player.x = 10
    player.y = 20
    renderer = FakeRenderer()
    scene = MapScene(tilemap, tilemap, player)

    scene.render(renderer)

    assert renderer.clears[-1] == scene.background_color
    assert tilemap.render_calls == [(renderer, (0, 0))]
    assert renderer.draw_images[-1][2] == (10, 20)


def test_camera_follows_player_and_clamps_to_bounds():
    tilemap = FakeTilemap(pixel_size=(640, 480))
    player = make_sprite()
    player.x = 200
    player.y = 150
    renderer = FakeRenderer()
    scene = MapScene(tilemap, tilemap, player)

    scene.render(renderer)

    assert tilemap.render_calls[-1][1] == (45, 35)
    assert renderer.draw_images[-1][2] == (155, 115)


def test_pan_camera_shifts_view_without_exposing_renderer():
    tilemap = FakeTilemap(pixel_size=(640, 480))
    player = make_sprite()
    player.x = 200
    player.y = 150
    renderer = FakeRenderer()
    scene = MapScene(tilemap, tilemap, player)

    scene.render(renderer)
    scene.pan_camera(50, -20)
    scene.render(renderer)

    assert tilemap.render_calls[-1][1] == (95, 15)
    assert renderer.draw_images[-1][2] == (105, 135)


def test_pan_camera_route_applies_multiple_steps_and_clamps():
    tilemap = FakeTilemap(pixel_size=(640, 480))
    player = make_sprite()
    player.x = 200
    player.y = 150
    renderer = FakeRenderer()
    scene = MapScene(tilemap, tilemap, player)

    scene.render(renderer)
    scene.pan_camera_route([(100, 0), (500, 0), (-50, -100)])
    scene.render(renderer)

    assert tilemap.render_calls[-1][1] == (320, 0)
    assert renderer.draw_images[-1][2] == (-120, 150)


def test_handle_interaction_invokes_manager_when_facing_npc():
    tilemap = FakeTilemap()
    player = make_sprite(InputCapturingSprite)
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    npc.y = player.spritesheet.frame_height + 2  # directly in front of the player
    controller = FakeController(npc=npc)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.handle_events([InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})])

    assert controller.interactions == [player]


def test_lifecycle_hooks_delegate_to_manager():
    tilemap = FakeTilemap()
    player = make_sprite()
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    controller = FakeController(npc=npc)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.on_enter()
    scene.on_exit()

    assert controller.enter_calls == 1
    assert controller.exit_calls == 1


def test_interaction_requires_facing_and_range():
    tilemap = FakeTilemap()
    player = make_sprite(InputCapturingSprite)
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    npc.x = player.spritesheet.frame_width + 15  # to the right but out of reach
    controller = FakeController(npc=npc)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.handle_events([InputEvent(type="KEYDOWN", payload={"key": Key.RIGHT})])

    scene.handle_events([InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})])

    assert controller.interactions == []
