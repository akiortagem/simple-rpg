import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.engine.async_scheduler import AsyncScheduler
from src.engine.scene_manager import SceneManager
from src.scenes import utils
from src.scenes.scenes import Scene, UIScene
from src.ui import Text


class DummyScene(Scene):
    def update(self, delta_time: float) -> None:
        return None

    def render(self, renderer) -> None:
        return None


class DummyUIScene(UIScene):
    def __init__(self) -> None:
        super().__init__()
        self.entered = False

    def build(self):
        return Text("Hello")

    def on_enter(self) -> None:
        self.entered = True


def test_spawn_ui_requires_registered_scene_manager():
    utils._scene_manager = None
    scheduler = AsyncScheduler()
    utils.register_scheduler(scheduler)

    with pytest.raises(RuntimeError, match="No SceneManager registered"):
        utils.spawn_ui(DummyUIScene())

    scheduler.loop.close()


def test_spawn_ui_rejects_non_ui_scene():
    manager = SceneManager(initial_scene=DummyScene())
    utils.register_scene_manager(manager)
    scheduler = AsyncScheduler()
    utils.register_scheduler(scheduler)

    with pytest.raises(TypeError, match="spawn_ui expects a UIScene"):
        utils.spawn_ui(DummyScene())  # type: ignore[arg-type]

    scheduler.loop.close()


def test_spawn_ui_pushes_overlay_scene():
    manager = SceneManager(initial_scene=DummyScene())
    utils.register_scene_manager(manager)
    scheduler = AsyncScheduler()
    utils.register_scheduler(scheduler)
    ui_scene = DummyUIScene()

    task = utils.spawn_ui(ui_scene)

    assert manager._overlay_scenes == [ui_scene]
    assert ui_scene.entered is True

    manager.pop_overlay(ui_scene)
    scheduler.loop.run_until_complete(task)
    scheduler.loop.close()
