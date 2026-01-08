import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import InputEvent, Renderer
from src.engine.scene_manager import SceneManager
from src.scenes import utils
from src.scenes.scenes import Scene, UIScene
from src.ui import Text


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
    def __init__(self, name: str, call_log: list[str]) -> None:
        self.name = name
        self.call_log = call_log

    def handle_events(self, events):
        self.call_log.append(f"events:{self.name}")

    def update(self, delta_time: float) -> None:
        self.call_log.append(f"update:{self.name}")

    def render(self, renderer: Renderer) -> None:
        self.call_log.append(f"render:{self.name}:{type(renderer).__name__}")


class StubUIScene(UIScene):
    def __init__(self, name: str, call_log: list[str]) -> None:
        super().__init__()
        self.name = name
        self.call_log = call_log
        self.exited = False

    def build(self):
        return Text("UI")

    def handle_events(self, events):
        self.call_log.append(f"events:{self.name}")

    def update(self, delta_time: float) -> None:
        self.call_log.append(f"update:{self.name}")

    def render(self, renderer: Renderer) -> None:
        self.call_log.append(f"render:{self.name}:{type(renderer).__name__}")

    def on_exit(self) -> None:
        self.exited = True


def test_spawn_ui_renders_overlay_after_base_scene():
    call_log: list[str] = []
    base = StubScene("base", call_log)
    manager = SceneManager(initial_scene=base)
    utils.register_scene_manager(manager)
    overlay = StubUIScene("overlay", call_log)
    renderer = DummyRenderer()

    utils.spawn_ui(overlay)
    manager.render(renderer)

    assert call_log == [
        "render:base:DummyRenderer",
        "render:overlay:_OverlayRenderer",
    ]


def test_spawn_ui_forwards_events_and_updates_to_overlay_then_base():
    call_log: list[str] = []
    base = StubScene("base", call_log)
    manager = SceneManager(initial_scene=base)
    utils.register_scene_manager(manager)
    overlay = StubUIScene("overlay", call_log)

    utils.spawn_ui(overlay)
    manager.handle_events([InputEvent(type="MOVE")])
    manager.update(0.25)

    assert call_log == [
        "events:overlay",
        "events:base",
        "update:overlay",
        "update:base",
    ]


def test_spawn_ui_overlay_removed_after_exit_request():
    call_log: list[str] = []
    base = StubScene("base", call_log)
    manager = SceneManager(initial_scene=base)
    utils.register_scene_manager(manager)
    overlay = StubUIScene("overlay", call_log)

    utils.spawn_ui(overlay)
    overlay.request_exit()
    manager.update(0.1)

    assert overlay.exited is True
    assert manager._overlay_scenes == []

    call_log.clear()
    manager.handle_events([InputEvent(type="MOVE")])

    assert call_log == ["events:base"]
