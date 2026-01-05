"""Application service to manage scene transitions.

Use ``SceneManager`` to set or swap ``Scene`` instances, forward input events,
tick updates, and render the active scene. It also owns the shared ``GameConfig``
passed into scenes.
"""

from __future__ import annotations

from typing import Optional, Sequence

from ..core.contracts import GameConfig, InputEvent, Renderer
from ..scenes.scenes import Scene


class SceneManager:
    """Tracks the current scene and coordinates lifecycle hooks."""

    def __init__(
        self,
        initial_scene: Scene | None = None,
        config: GameConfig | None = None,
    ) -> None:
        self._current_scene: Scene | None = None
        self._config = config or GameConfig()
        if initial_scene is not None:
            self.set_scene(initial_scene)

    @property
    def current_scene(self) -> Optional[Scene]:
        """Return the active scene, if any."""
        return self._current_scene

    @property
    def config(self) -> GameConfig:
        """Return the shared game configuration."""
        return self._config

    def set_scene(self, scene: Scene) -> None:
        """Replace the active scene and trigger lifecycle hooks."""
        if self._current_scene is not None:
            self._current_scene.on_exit()
        scene.config = self._config
        self._current_scene = scene
        self._current_scene.on_enter()

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        """Forward input events to the active scene."""
        if self._current_scene is not None:
            self._current_scene.handle_events(events)

    def update(self, delta_time: float) -> None:
        """Advance the active scene by ``delta_time`` seconds."""
        if self._current_scene is not None:
            self._current_scene.update(delta_time)

    def render(self, renderer: Renderer) -> None:
        """Render the active scene using the provided renderer."""
        if self._current_scene is not None:
            self._current_scene.render(renderer)
