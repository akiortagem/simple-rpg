"""Declarative, immutable UI components and layout helpers.

Compose UI trees from ``UIElement`` implementations like ``Column``,
``Container``, and ``Text``. Use ``UIController`` to translate input events into
menu focus, and feed layouts into ``UIRenderer`` via ``UIScene``.
"""

from .base import LayoutNode, Rect, Size, UIElement, UIElements
from .border import Border
from .center import Center
from .column import Column
from .container import Container
from .controller import UIController
from .dialog import Dialog
from .menu import Menu
from .menu_choice import MenuChoice
from .spacing import Spacing
from .text import Text

__all__ = [
    "Border",
    "Center",
    "Column",
    "Container",
    "Dialog",
    "LayoutNode",
    "Menu",
    "MenuChoice",
    "Rect",
    "Size",
    "Spacing",
    "Text",
    "UIController",
    "UIElement",
    "UIElements",
]
