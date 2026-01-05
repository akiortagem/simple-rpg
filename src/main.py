"""Convenience helpers for wiring up Simple RPG with pygame infrastructure."""

from __future__ import annotations

import pygame

from src.core.contracts import GameConfig
from src.engine.game_loop import GameLoop
from src.engine.scene_manager import SceneManager
from src.io.pygame_adapter import (
    PygameClock,
    PygameEventSource,
    PygameRenderer,
)
from src.scenes.scenes import DemoScene, Scene


def build_game(
    width: int = 800,
    height: int = 600,
    title: str = "Simple RPG",
    initial_scene: Scene | None = None,
    debug_collision: bool = False,
) -> GameLoop:
    """Wire up the game loop with pygame infrastructure.

    Parameters
    ----------
    width: int
        Desired window width in pixels.
    height: int
        Desired window height in pixels.
    title: str
        Title for the pygame window caption.
    initial_scene: Scene | None
        The scene to show when the loop starts. If omitted, ``DemoScene``
        will be used as a placeholder.
    debug_collision: bool
        Whether scenes should visualize collision debugging information.
    """
    pygame.init()

    renderer = PygameRenderer((width, height), title)
    events = PygameEventSource()
    clock = PygameClock()

    scene_manager = SceneManager(
        initial_scene or DemoScene(),
        config=GameConfig(debug_collision=debug_collision),
    )
    return GameLoop(scene_manager=scene_manager, renderer=renderer, events=events, clock=clock)
