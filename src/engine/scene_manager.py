"""Application service to manage scene transitions.

Use ``SceneManager`` to set or swap ``Scene`` instances, forward input events,
tick updates, and render the active scene. It also owns the shared ``GameConfig``
passed into scenes.
"""

from __future__ import annotations

from typing import Optional, Sequence

from ..core.contracts import GameConfig, InputEvent, Renderer
from ..scenes.scenes import LayeredScene, Scene, UIScene


class SceneManager:
    """Tracks the current scene and coordinates lifecycle hooks."""

    def __init__(
        self,
        initial_scene: Scene | None = None,
        config: GameConfig | None = None,
    ) -> None:
        self._current_scene: Scene | None = None
        self._overlay_scenes: list[Scene] = []
        self._blocking_overlays: set[Scene] = set()
        self._config = config or GameConfig()
        self._exit_requested = False
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
        self.clear_overlays()
        if self._current_scene is not None:
            self._current_scene.on_exit()
        scene.config = self._config
        self._current_scene = scene
        self._exit_requested = False
        self._current_scene.on_enter()

    def push_overlay(self, scene: Scene) -> None:
        """Add an overlay scene above the current scene."""
        scene.config = self._config
        self._overlay_scenes.append(scene)
        scene.on_enter()

    def push_scene(self, scene: Scene) -> None:
        """Pause the current scene and push a blocking scene above it."""
        if self._current_scene is None:
            self.set_scene(scene)
            return
        self.push_overlay(scene)
        self._blocking_overlays.add(scene)

    def pop_overlay(self, scene: Scene | None = None) -> Scene | None:
        """Remove the top-most or specified overlay scene, if any."""
        if not self._overlay_scenes:
            return None
        if scene is None:
            scene = self._overlay_scenes.pop()
        else:
            if scene not in self._overlay_scenes:
                return None
            self._overlay_scenes.remove(scene)
        self._finalize_overlay(scene)
        return scene

    def clear_overlays(self) -> None:
        """Remove all overlay scenes, invoking exit hooks."""
        while self._overlay_scenes:
            scene = self._overlay_scenes.pop()
            self._finalize_overlay(scene)

    def should_exit(self) -> bool:
        """Return whether any active scene requested exiting the game loop."""
        if self._exit_requested:
            return True
        if self._current_scene is not None and self._current_scene.should_exit():
            return True
        return any(scene.should_exit() for scene in self._overlay_scenes)

    def _active_scene(self) -> Scene | None:
        if self._current_scene is None:
            return None
        if not self._overlay_scenes:
            return self._current_scene
        overlays_top_to_bottom = list(reversed(self._overlay_scenes))
        return LayeredScene([*overlays_top_to_bottom, self._current_scene])

    def _scenes_for_input_update(self) -> list[Scene]:
        if self._current_scene is None:
            return []
        if not self._overlay_scenes:
            return [self._current_scene]
        overlays_top_to_bottom = list(reversed(self._overlay_scenes))
        if not self._blocking_overlays:
            return [*overlays_top_to_bottom, self._current_scene]
        for index, scene in enumerate(overlays_top_to_bottom):
            if scene in self._blocking_overlays:
                return overlays_top_to_bottom[: index + 1]
        return overlays_top_to_bottom

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        """Forward input events to the active scene."""
        active_scenes = self._scenes_for_input_update()
        for scene in active_scenes:
            scene.handle_events(events)

    def allows_global_keypress(self) -> bool:
        """Return whether the global key handler should run this frame."""
        if self._overlay_scenes:
            return False
        if self._current_scene is None:
            return True
        return not isinstance(self._current_scene, UIScene)

    def update(self, delta_time: float) -> None:
        """Advance the active scene by ``delta_time`` seconds."""
        active_scenes = self._scenes_for_input_update()
        if not active_scenes:
            return
        for scene in active_scenes:
            scene.update(delta_time)
        if self._overlay_scenes:
            remaining: list[Scene] = []
            for scene in self._overlay_scenes:
                if scene.should_exit():
                    self._exit_requested = True
                    self._finalize_overlay(scene)
                else:
                    remaining.append(scene)
            self._overlay_scenes = remaining

    def render(self, renderer: Renderer) -> None:
        """Render the active scene using the provided renderer."""
        active_scene = self._active_scene()
        if active_scene is not None:
            active_scene.render(renderer)

    def _finalize_overlay(self, scene: Scene) -> None:
        self._blocking_overlays.discard(scene)
        scene.on_exit()
        if isinstance(scene, UIScene):
            scene._resolve_pop_future()
