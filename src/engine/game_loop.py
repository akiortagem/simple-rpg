"""Application-level game loop orchestrating domain and infrastructure.

``GameLoop`` connects a ``SceneManager`` with framework adapters that implement
``Renderer``, ``EventSource``, and ``TimeSource``. Call ``GameLoop.run`` to
start the frame loop, which polls events, advances the active scene, and
renders each frame.
"""

from __future__ import annotations

from typing import Callable

from ..core.contracts import EventSource, Renderer, TimeSource
from .async_scheduler import AsyncScheduler
from .scene_manager import SceneManager


class GameLoop:
    """Central loop that wires together input, domain logic, and rendering."""

    def __init__(
        self,
        scene_manager: SceneManager,
        renderer: Renderer,
        events: EventSource,
        clock: TimeSource,
        target_fps: int = 60,
        global_on_keypress: Callable[[str], None] | None = None,
        scheduler: AsyncScheduler | None = None,
    ) -> None:
        self._scene_manager = scene_manager
        self._renderer = renderer
        self._events = events
        self._clock = clock
        self._target_fps = target_fps
        self._global_on_keypress = global_on_keypress
        self._scheduler = scheduler or AsyncScheduler()
        from ..scenes.utils import register_scheduler

        register_scheduler(self._scheduler)

    def run(self) -> None:
        """Run the main loop until a quit event or scene exit request."""
        running = True
        while running:
            event_batch = self._events.poll()
            if any(event.type == "QUIT" for event in event_batch):
                running = False
            if (
                self._global_on_keypress
                and self._scene_manager.allows_global_keypress()
            ):
                self._scene_manager.handle_events(event_batch)
                for event in event_batch:
                    if event.type != "KEYDOWN" or not event.payload:
                        continue
                    if event.payload.get("handled"):
                        continue
                    key = event.payload.get("key")
                    if isinstance(key, str):
                        self._global_on_keypress(key)
            else:
                self._scene_manager.handle_events(event_batch)

            if self._scene_manager.should_exit():
                running = False
                continue

            delta_time = self._clock.tick(self._target_fps)
            self._scheduler.tick()
            self._scene_manager.update(delta_time)

            self._scene_manager.render(self._renderer)
            self._renderer.present()
