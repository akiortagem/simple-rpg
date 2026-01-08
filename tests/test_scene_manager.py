import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import GameConfig, InputEvent, Renderer
from src.engine.scene_manager import SceneManager
from src.scenes.scenes import Scene


@dataclass
class DummyRenderer(Renderer):
    width: int = 320
    height: int = 200

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def clear(self, color):
        return None

    def draw_rect(self, color, rect):
        return None

    def draw_rect_outline(self, color, rect, width: int = 1):
        return None

    def draw_image(self, image, source_rect, destination):
        return None

    def draw_text(self, text, position, color, font_size: int = 32, center: bool = False):
        return None

    def present(self) -> None:
        return None


class StubScene(Scene):
    def __init__(self, name: str) -> None:
        self.name = name
        self.entered = False
        self.exited = False
        self.events: list[InputEvent] = []
        self.updated: list[float] = []
        self.rendered_with: list[Renderer] = []

    def on_enter(self) -> None:
        self.entered = True

    def on_exit(self) -> None:
        self.exited = True

    def handle_events(self, events):
        self.events = list(events)

    def update(self, delta_time: float) -> None:
        self.updated.append(delta_time)

    def render(self, renderer: Renderer) -> None:
        self.rendered_with.append(renderer)


class OrderedScene(Scene):
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def handle_events(self, events):
        self.calls.append(f"events:{self.name}")

    def update(self, delta_time: float) -> None:
        self.calls.append(f"update:{self.name}")

    def render(self, renderer: Renderer) -> None:
        return None


class ExitScene(StubScene):
    def update(self, delta_time: float) -> None:
        super().update(delta_time)
        self.request_exit()


def test_set_scene_triggers_lifecycle_and_assigns_config():
    config = GameConfig(debug_collision=True)
    first = StubScene("first")
    manager = SceneManager(initial_scene=first, config=config)

    assert first.entered is True
    assert first.config is config

    second = StubScene("second")
    manager.set_scene(second)

    assert first.exited is True
    assert second.entered is True
    assert second.config is config
    assert manager.current_scene is second


def test_scene_manager_forwards_events_update_and_render():
    scene = StubScene("active")
    manager = SceneManager(initial_scene=scene)
    events = [InputEvent(type="MOVE")]
    renderer = DummyRenderer()

    manager.handle_events(events)
    manager.update(0.25)
    manager.render(renderer)

    assert scene.events == events
    assert scene.updated == [0.25]
    assert scene.rendered_with == [renderer]


def test_overlay_scenes_receive_config_and_are_ordered():
    config = GameConfig()
    calls: list[str] = []
    base = OrderedScene("base", calls)
    overlay_one = OrderedScene("overlay_one", calls)
    overlay_two = OrderedScene("overlay_two", calls)
    manager = SceneManager(initial_scene=base, config=config)

    manager.push_overlay(overlay_one)
    manager.push_overlay(overlay_two)

    assert overlay_one.config is config
    assert overlay_two.config is config

    manager.handle_events([])
    manager.update(0.5)

    assert calls == [
        "events:overlay_two",
        "events:overlay_one",
        "events:base",
        "update:overlay_two",
        "update:overlay_one",
        "update:base",
    ]


def test_overlay_scene_exits_after_update():
    calls: list[str] = []
    base = OrderedScene("base", calls)
    overlay = ExitScene("overlay")
    manager = SceneManager(initial_scene=base)

    manager.push_overlay(overlay)
    manager.update(0.1)

    assert overlay.exited is True

    calls.clear()
    manager.handle_events([])

    assert calls == ["events:base"]


def test_overlay_exit_request_sets_manager_exit_flag():
    base = OrderedScene("base", [])
    overlay = StubScene("overlay")
    manager = SceneManager(initial_scene=base)

    manager.push_overlay(overlay)
    overlay.request_exit()

    assert manager.should_exit() is True

    manager.update(0.1)

    assert overlay.exited is True
    assert manager.should_exit() is True
