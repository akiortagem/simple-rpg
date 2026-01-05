"""Application-level game loop orchestrating domain and infrastructure.

``GameLoop`` connects a ``SceneManager`` with framework adapters that implement
``Renderer``, ``EventSource``, and ``TimeSource``. Call ``GameLoop.run`` to
start the frame loop, which polls events, advances the active scene, and
renders each frame.
"""

from __future__ import annotations

from ..core.contracts import EventSource, Renderer, TimeSource
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
    ) -> None:
        self._scene_manager = scene_manager
        self._renderer = renderer
        self._events = events
        self._clock = clock
        self._target_fps = target_fps

    def run(self) -> None:
        """Run the main loop until a quit event or scene exit request."""
        running = True
        while running:
            event_batch = self._events.poll()
            if any(event.type == "QUIT" for event in event_batch):
                running = False

            self._scene_manager.handle_events(event_batch)

            current_scene = self._scene_manager.current_scene
            if current_scene is not None and current_scene.should_exit():
                running = False
                continue

            delta_time = self._clock.tick(self._target_fps)
            self._scene_manager.update(delta_time)

            self._scene_manager.render(self._renderer)
            self._renderer.present()
