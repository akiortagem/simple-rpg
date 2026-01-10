"""Runtime orchestration utilities for the game loop and scene flow.

Import ``GameLoop`` and ``SceneManager`` from here when wiring the engine
startup. ``SceneManager`` owns the active ``Scene`` while ``GameLoop.run``
coordinates input polling, scene updates, and rendering.
"""

from .async_scheduler import AsyncScheduler
from .game_loop import GameLoop
from .scene_manager import SceneManager

__all__ = ["AsyncScheduler", "GameLoop", "SceneManager"]
