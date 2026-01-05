import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import GameConfig, InputEvent, Renderer
from src.scenes.scenes import LayeredScene, Scene


@dataclass
class DummyRenderer(Renderer):
    width: int = 320
    height: int = 200
    clears: list[tuple[int, int, int]] | None = None

    def __post_init__(self) -> None:
        if self.clears is None:
            self.clears = []

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def clear(self, color):
        self.clears.append(color)

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
    def __init__(self, name: str, record: list[str]) -> None:
        self.name = name
        self.record = record
        self.entered = False
        self.exited = False

    def on_enter(self) -> None:
        self.entered = True
        self.record.append(f"{self.name}:enter")

    def on_exit(self) -> None:
        self.exited = True
        self.record.append(f"{self.name}:exit")

    def handle_events(self, events) -> None:
        self.record.append(f"{self.name}:events")

    def update(self, delta_time: float) -> None:
        self.record.append(f"{self.name}:update")

    def render(self, renderer: Renderer) -> None:
        renderer.clear((0, 0, 0))
        self.record.append(f"{self.name}:render")


def test_layered_scene_propagates_config_and_lifecycle():
    record: list[str] = []
    top = StubScene("top", record)
    bottom = StubScene("bottom", record)
    config = GameConfig(debug_collision=True)
    layered = LayeredScene([top, bottom])
    layered.config = config

    layered.on_enter()

    assert top.entered is True
    assert bottom.entered is True
    assert top.config is config
    assert bottom.config is config

    layered.on_exit()

    assert top.exited is True
    assert bottom.exited is True


def test_layered_scene_forwards_events_and_updates_in_order():
    record: list[str] = []
    top = StubScene("top", record)
    middle = StubScene("middle", record)
    bottom = StubScene("bottom", record)
    layered = LayeredScene([top, middle, bottom])

    layered.handle_events([InputEvent(type="MOVE")])
    layered.update(0.1)

    assert record == [
        "top:events",
        "middle:events",
        "bottom:events",
        "top:update",
        "middle:update",
        "bottom:update",
    ]


def test_layered_scene_renders_bottom_to_top_with_overlay_clear_no_op():
    record: list[str] = []
    top = StubScene("top", record)
    middle = StubScene("middle", record)
    bottom = StubScene("bottom", record)
    layered = LayeredScene([top, middle, bottom])
    renderer = DummyRenderer()

    layered.render(renderer)

    assert record == [
        "bottom:render",
        "middle:render",
        "top:render",
    ]
    assert renderer.clears == [(0, 0, 0)]


def test_layered_scene_should_exit_when_child_requests_exit():
    record: list[str] = []
    top = StubScene("top", record)
    bottom = StubScene("bottom", record)
    layered = LayeredScene([top, bottom])

    assert layered.should_exit() is False

    bottom.request_exit()

    assert layered.should_exit() is True
