"""Entry point for the Simple RPG Pygame application."""

from __future__ import annotations

import pygame

from src.game.application.game_loop import GameLoop
from src.game.application.scene_manager import SceneManager
from src.game.domain.scenes import DemoScene
from src.game.infrastructure.pygame_adapter import (
    PygameClock,
    PygameEventSource,
    PygameRenderer,
)


def build_game(width: int = 800, height: int = 600, title: str = "Simple RPG") -> GameLoop:
    """Wire up the game loop with pygame infrastructure."""
    pygame.init()

    renderer = PygameRenderer((width, height), title)
    events = PygameEventSource()
    clock = PygameClock()

    scene_manager = SceneManager(DemoScene())
    return GameLoop(scene_manager=scene_manager, renderer=renderer, events=events, clock=clock)


def main() -> None:
    """Initialize the game and run the cleanly-structured loop."""
    game = build_game()
    try:
        game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
