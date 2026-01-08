import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.abspath("."))

from src.ui.base import LayoutNode, Rect, Size
from src.ui.center import Center


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
