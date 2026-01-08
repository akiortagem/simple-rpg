import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import InputEvent, Renderer
from src.scenes.scenes import LayeredScene, Scene


@dataclass
class DummyRenderer(Renderer):
    width: int = 320
    height: int = 200

    def __post_init__(self) -> None:
        self.clear_calls: list[object] = []

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def clear(self, color):
        self.clear_calls.append(color)

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
        renderer.clear(self.name)


def test_layered_scene_renders_bottom_to_top_and_clears_once():
    call_log: list[str] = []
    top = StubScene("top", call_log)
    bottom = StubScene("bottom", call_log)
    layered = LayeredScene([top, bottom])
    renderer = DummyRenderer()

    layered.render(renderer)

    assert call_log == [
        "render:bottom:DummyRenderer",
        "render:top:_OverlayRenderer",
    ]
    assert renderer.clear_calls == ["bottom"]


def test_layered_scene_forwards_events_and_updates_in_order():
    call_log: list[str] = []
    top = StubScene("top", call_log)
    middle = StubScene("middle", call_log)
    bottom = StubScene("bottom", call_log)
    layered = LayeredScene([top, middle, bottom])

    layered.handle_events([InputEvent(type="MOVE")])
    layered.update(0.5)

    assert call_log == [
        "events:top",
        "events:middle",
        "events:bottom",
        "update:top",
        "update:middle",
        "update:bottom",
    ]
