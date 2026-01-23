"""Minimal intro menu example built on top of simple-rpg."""

from __future__ import annotations

from src.core.contracts import Key
from src.scenes.utils import push_scene
from src.ui import *
from src.main import build_game

from .pause_menus import PauseGameMenuDialog
from .intro_scene import IntroScene

def global_on_keypress_handlers(key:Key) -> None:
    if key == Key.PAUSE:
        push_scene(PauseGameMenuDialog())

def main() -> None:
    game = build_game(
        title="Simple RPG Intro", 
        initial_scene=IntroScene(),
        global_on_keypress=global_on_keypress_handlers # Only handles when there are no other handlers handling it
    )
    game.run()



if __name__ == "__main__":
    main()
