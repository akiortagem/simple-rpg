import asyncio
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


class DummyHookScene(Scene):
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def on_enter(self) -> None:
        self.entered = True

    def on_exit(self) -> None:
        self.exited = True

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


def test_spawn_ui_uses_running_loop_without_scheduler():
    manager = SceneManager(initial_scene=DummyScene())
    utils.register_scene_manager(manager)
    utils._scheduler = None
    ui_scene = DummyUIScene()

    async def run_test() -> None:
        task = utils.spawn_ui(ui_scene)

        assert task.get_loop() is asyncio.get_running_loop()
        assert manager._overlay_scenes == [ui_scene]

        manager.pop_overlay(ui_scene)
        await task

    asyncio.run(run_test())


def test_to_scene_requires_registered_scene_manager():
    utils._scene_manager = None

    with pytest.raises(RuntimeError, match="No SceneManager registered"):
        utils.to_scene(DummyScene())


def test_to_scene_rejects_non_scene():
    manager = SceneManager(initial_scene=DummyScene())
    utils.register_scene_manager(manager)

    with pytest.raises(TypeError, match="to_scene expects a Scene"):
        utils.to_scene("not a scene")  # type: ignore[arg-type]


def test_to_scene_sets_scene_and_triggers_hooks():
    initial_scene = DummyHookScene()
    manager = SceneManager(initial_scene=initial_scene)
    utils.register_scene_manager(manager)
    next_scene = DummyHookScene()

    assert initial_scene.entered is True

    utils.to_scene(next_scene)

    assert manager.current_scene is next_scene
    assert initial_scene.exited is True
    assert next_scene.entered is True
