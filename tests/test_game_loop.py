import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import InputEvent, Renderer
from src.engine.game_loop import GameLoop


class StubScene:
    def __init__(self, should_exit: bool) -> None:
        self._should_exit = should_exit

    def should_exit(self) -> bool:
        return self._should_exit


class RecordingSceneManager:
    def __init__(self, scene: StubScene, order: list[str]) -> None:
        self.current_scene = scene
        self._order = order

    def handle_events(self, events):
        self._order.append("handle_events")

    def update(self, delta_time: float) -> None:
        self._order.append("update")

    def render(self, renderer: Renderer) -> None:
        self._order.append("render")

    def should_exit(self) -> bool:
        return self.current_scene.should_exit()


class RecordingGlobalSceneManager:
    def __init__(
        self,
        allow_global: bool,
        order: list[str],
        mark_handled: bool = False,
    ) -> None:
        self.current_scene = StubScene(should_exit=False)
        self._allow_global = allow_global
        self._order = order
        self._mark_handled = mark_handled

    def allows_global_keypress(self) -> bool:
        return self._allow_global

    def handle_events(self, events):
        self._order.append("handle_events")
        if self._mark_handled:
            for event in events:
                if event.payload is not None:
                    event.payload["handled"] = True

    def update(self, delta_time: float) -> None:
        self._order.append("update")

    def render(self, renderer: Renderer) -> None:
        self._order.append("render")

    def should_exit(self) -> bool:
        return self.current_scene.should_exit()


@dataclass
class RecordingRenderer(Renderer):
    order: list[str]

    @property
    def size(self) -> tuple[int, int]:
        return (320, 200)

    def clear(self, color) -> None:
        return None

    def draw_rect(self, color, rect) -> None:
        return None

    def draw_rect_outline(self, color, rect, width: int = 1) -> None:
        return None

    def draw_image(self, image, source_rect, destination) -> None:
        return None

    def draw_text(self, text, position, color, font_size: int = 32, center: bool = False) -> None:
        return None

    def present(self) -> None:
        self.order.append("present")


class RecordingEventSource:
    def __init__(self, events, order: list[str]) -> None:
        self._events = events
        self._order = order
        self._polled = False

    def poll(self):
        self._order.append("poll")
        if self._polled:
            return []
        self._polled = True
        return self._events


class RecordingTimeSource:
    def __init__(self, order: list[str]) -> None:
        self._order = order

    def tick(self, target_fps: int) -> float:
        self._order.append("tick")
        return 0.016


def test_game_loop_runs_update_and_render_in_order():
    order: list[str] = []
    scene = StubScene(should_exit=False)
    manager = RecordingSceneManager(scene, order)
    renderer = RecordingRenderer(order)
    events = [InputEvent(type="QUIT")]
    game_loop = GameLoop(
        manager,
        renderer,
        RecordingEventSource(events, order),
        RecordingTimeSource(order),
    )

    game_loop.run()

    assert order == ["poll", "handle_events", "tick", "update", "render", "present"]


def test_game_loop_skips_update_and_render_when_scene_exits():
    order: list[str] = []
    scene = StubScene(should_exit=True)
    manager = RecordingSceneManager(scene, order)
    renderer = RecordingRenderer(order)
    game_loop = GameLoop(
        manager,
        renderer,
        RecordingEventSource([], order),
        RecordingTimeSource(order),
    )

    game_loop.run()

    assert order == ["poll", "handle_events"]


def test_game_loop_calls_global_on_keypress_when_allowed():
    order: list[str] = []
    manager = RecordingGlobalSceneManager(allow_global=True, order=order)
    renderer = RecordingRenderer(order)
    events = [
        InputEvent(type="KEYDOWN", payload={"key": "A"}),
        InputEvent(type="QUIT"),
    ]

    def record_global(key: str) -> None:
        order.append(f"global:{key}")

    game_loop = GameLoop(
        manager,
        renderer,
        RecordingEventSource(events, order),
        RecordingTimeSource(order),
        global_on_keypress=record_global,
    )

    game_loop.run()

    assert order == [
        "poll",
        "handle_events",
        "global:A",
        "tick",
        "update",
        "render",
        "present",
    ]


def test_game_loop_skips_global_on_keypress_when_handled():
    order: list[str] = []
    manager = RecordingGlobalSceneManager(
        allow_global=True,
        order=order,
        mark_handled=True,
    )
    renderer = RecordingRenderer(order)
    events = [
        InputEvent(type="KEYDOWN", payload={"key": "A"}),
        InputEvent(type="QUIT"),
    ]

    def record_global(key: str) -> None:
        order.append(f"global:{key}")

    game_loop = GameLoop(
        manager,
        renderer,
        RecordingEventSource(events, order),
        RecordingTimeSource(order),
        global_on_keypress=record_global,
    )

    game_loop.run()

    assert "global:A" not in order


def test_game_loop_skips_global_on_keypress_when_disallowed():
    order: list[str] = []
    manager = RecordingGlobalSceneManager(allow_global=False, order=order)
    renderer = RecordingRenderer(order)
    events = [
        InputEvent(type="KEYDOWN", payload={"key": "A"}),
        InputEvent(type="QUIT"),
    ]

    def record_global(key: str) -> None:
        order.append(f"global:{key}")

    game_loop = GameLoop(
        manager,
        renderer,
        RecordingEventSource(events, order),
        RecordingTimeSource(order),
        global_on_keypress=record_global,
    )

    game_loop.run()

    assert "global:A" not in order
