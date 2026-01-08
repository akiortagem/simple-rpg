from __future__ import annotations

from typing import Optional

from src.engine.scene_manager import SceneManager

from .scenes import UIScene

_scene_manager: Optional[SceneManager] = None


def register_scene_manager(scene_manager: SceneManager) -> None:
    global _scene_manager
    _scene_manager = scene_manager


def spawn_ui(ui_scene: UIScene) -> None:
    if not isinstance(ui_scene, UIScene):
        raise TypeError("spawn_ui expects a UIScene instance.")
    if _scene_manager is None:
        raise RuntimeError("No SceneManager registered. Call register_scene_manager first.")
    _scene_manager.push_overlay(ui_scene)
