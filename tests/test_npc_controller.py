import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.game.domain.contracts import InputEvent, Key
from src.game.domain.npc_controller import NPCRoute, NPCController
from src.game.domain.scenes import MapScene
from src.game.domain.sprites import NPCMapSprite, PCMapSprite, SpriteSheetDescriptor


class FakeTilemap:
    def __init__(self):
        self.pixel_size = (200, 200)
        self.blocked = False

    def render(self, renderer, camera_offset=(0, 0)):
        return None

    def collides(self, hitbox):
        return self.blocked


def make_pc(name="hero"):
    descriptor = SpriteSheetDescriptor(
        image="image",
        frame_width=10,
        frame_height=10,
        columns=1,
        animations={"idle": {"down": [0]}, "walk": {"right": [0]}},
    )
    return PCMapSprite(name=name, spritesheet=descriptor)


def make_npc(name="npc"):
    descriptor = SpriteSheetDescriptor(
        image="image",
        frame_width=10,
        frame_height=10,
        columns=1,
        animations={"idle": {"down": [0]}, "walk": {"right": [0]}},
    )
    return NPCMapSprite(name=name, spritesheet=descriptor)


def test_default_route_moves_back_and_forth():
    tilemap = FakeTilemap()
    player = make_pc("player")
    npc = make_npc("npc")
    controller = NPCController(npc=npc, speed=40.0)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.on_enter()
    scene.update(1.0)
    first_leg_position = npc.x

    scene.update(1.0)

    assert first_leg_position < 0, "Default route should start by moving left"
    assert npc.x > first_leg_position, "Second leg should head back to the right"


def test_route_controller_moves_along_waypoints_and_loops():
    tilemap = FakeTilemap()
    player = make_pc("player")
    npc = make_npc("npc")
    route = NPCRoute(waypoints=[(10.0, 0.0), (10.0, 10.0)], loop=True, wait_time=0.0)
    controller = NPCController(npc=npc, route=route, speed=10.0)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.on_enter()
    scene.update(1.0)
    assert pytest.approx((npc.x, npc.y), rel=1e-4) == (10.0, 0.0)

    scene.update(1.0)
    assert pytest.approx((npc.x, npc.y), rel=1e-4) == (10.0, 10.0)

    # Third update should bring NPC back toward the first waypoint due to looping
    scene.update(1.0)
    assert npc.x < 10.0 or npc.y < 10.0


def test_route_controller_respects_wait_time_at_waypoints():
    tilemap = FakeTilemap()
    player = make_pc("player")
    npc = make_npc("npc")
    route = NPCRoute(waypoints=[(5.0, 0.0)], loop=False, wait_time=0.5)
    controller = NPCController(npc=npc, route=route, speed=10.0)
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.on_enter()
    scene.update(0.5)
    assert pytest.approx((npc.x, npc.y), rel=1e-4) == (5.0, 0.0)

    # Wait timer should keep NPC paused when elapsed is below wait_time
    scene.update(0.25)
    assert npc.velocity == (0.0, 0.0)


def test_empty_route_keeps_npc_stationary():
    tilemap = FakeTilemap()
    player = make_pc("player")
    npc = make_npc("npc")
    controller = NPCController(npc=npc, route=NPCRoute(waypoints=()))
    scene = MapScene(tilemap, tilemap, player, [controller])

    scene.on_enter()
    scene.update(1.0)

    assert npc.x == 0.0
    assert npc.velocity == (0.0, 0.0)
