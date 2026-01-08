import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.ui.base import LayoutNode, Rect, Size
from src.ui.border import Border
from src.ui.center import Center
from src.ui.container import Container


@dataclass(frozen=True)
class FixedElement:
    size: Size

    def measure(self, bounds: Size) -> Size:
        return self.size

    def layout(self, bounds: Rect) -> LayoutNode:
        return LayoutNode(self, bounds)


def test_center_layout_centers_child():
    child = FixedElement(Size(10, 4))
    center = Center(child)
    layout = center.layout(Rect(0, 0, 30, 20))

    assert layout.children[0].rect == Rect(10, 8, 10, 4)


def test_center_layout_clamps_child_size():
    child = FixedElement(Size(50, 40))
    center = Center(child)
    layout = center.layout(Rect(5, 5, 30, 20))

    assert layout.children[0].rect == Rect(5, 5, 30, 20)


def test_container_measure_prefers_explicit_size():
    container = Container(width=12, height=8)

    assert container.measure(Size(20, 20)) == Size(12, 8)


def test_container_measure_defaults_to_bounds():
    child = FixedElement(Size(4, 2))
    container = Container(content=child)

    assert container.measure(Size(20, 15)) == Size(20, 15)


def test_center_layout_uses_container_measure():
    container = Container(width=10, height=6)
    center = Center(container)
    layout = center.layout(Rect(0, 0, 30, 20))

    assert layout.children[0].rect == Rect(10, 7, 10, 6)


def test_container_layout_respects_border_inset():
    child = FixedElement(Size(10, 4))
    container = Container(border=Border(width=2), content=child, width=12, height=8)
    layout = container.layout(Rect(0, 0, 30, 20))

    assert layout.rect == Rect(0, 0, 12, 8)
    assert layout.children[0].rect == Rect(0, 0, 12, 8)
    assert layout.children[1].rect == Rect(2, 2, 8, 4)
