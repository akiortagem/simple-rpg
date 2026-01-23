import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.core.contracts import InputEvent, Key
from src.ui.base import LayoutNode, Rect, Size
from src.ui.column import Column
from src.ui.controller import UIController
from src.ui.keypress_detector import KeypressDetector
from src.ui.text import Text


@dataclass(frozen=True)
class FixedElement:
    size: Size

    def measure(self, bounds: Size) -> Size:
        return self.size

    def layout(self, bounds: Rect) -> LayoutNode:
        return LayoutNode(self, bounds)


def test_keypress_detector_forwards_layout_to_child():
    child = FixedElement(Size(5, 2))
    detector = KeypressDetector(content=child, on_interact=lambda: None)

    layout = detector.layout(Rect(0, 0, 12, 6))

    assert layout.children[0].rect == Rect(0, 0, 12, 6)
    assert layout.children[0].element is child


def test_keypress_detector_calls_on_interact_for_enter():
    calls: list[str] = []
    detector = KeypressDetector(
        content=Text("Press"),
        on_interact=lambda: calls.append("hit"),
    )
    controller = UIController()

    controller.handle_events(
        [InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})],
        detector,
    )

    assert calls == ["hit"]


def test_keypress_detector_ignores_other_keys():
    calls: list[str] = []
    detector = KeypressDetector(
        content=Text("Press"),
        on_interact=lambda: calls.append("hit"),
    )
    controller = UIController()

    controller.handle_events(
        [InputEvent(type="KEYDOWN", payload={"key": Key.UP})],
        detector,
    )

    assert calls == []


def test_keypress_detector_only_fires_in_active_tree():
    calls: list[str] = []
    detector = KeypressDetector(
        content=Text("Press"),
        on_interact=lambda: calls.append("hit"),
    )
    controller = UIController()

    controller.handle_events(
        [InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})],
        Column(contents=(Text("Other"),)),
    )

    assert calls == []

    controller.handle_events(
        [InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})],
        Column(contents=(detector,)),
    )

    assert calls == ["hit"]


def test_keypress_detector_on_keypress_marks_event_handled():
    calls: list[str] = []

    def handle_key(key: str) -> bool:
        calls.append(key)
        return True

    detector = KeypressDetector(
        content=Text("Press"),
        on_keypress=handle_key,
    )
    controller = UIController()
    event = InputEvent(type="KEYDOWN", payload={"key": "X"})

    controller.handle_events([event], detector)

    assert calls == ["X"]
    assert event.payload["handled"] is True


def test_keypress_detector_on_keypress_allows_unhandled_events():
    detector = KeypressDetector(
        content=Text("Press"),
        on_keypress=lambda key: False,
    )
    controller = UIController()
    event = InputEvent(type="KEYDOWN", payload={"key": "X"})

    controller.handle_events([event], detector)

    assert event.payload.get("handled") is None
