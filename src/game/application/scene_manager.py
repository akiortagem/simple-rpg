"""Application service to manage scene transitions."""

from __future__ import annotations

from typing import Optional, Sequence

from ..domain.contracts import GameConfig, InputEvent, Renderer
from ..domain.scenes import Scene


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
        return self._current_scene

    @property
    def config(self) -> GameConfig:
        return self._config

    def set_scene(self, scene: Scene) -> None:
        if self._current_scene is not None:
            self._current_scene.on_exit()
        scene.config = self._config
        self._current_scene = scene
        self._current_scene.on_enter()

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        if self._current_scene is not None:
            self._current_scene.handle_events(events)

    def update(self, delta_time: float) -> None:
        if self._current_scene is not None:
            self._current_scene.update(delta_time)

    def render(self, renderer: Renderer) -> None:
        if self._current_scene is not None:
            self._current_scene.render(renderer)
