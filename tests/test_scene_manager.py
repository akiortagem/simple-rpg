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
