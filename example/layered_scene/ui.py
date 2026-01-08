from __future__ import annotations

from src.core.contracts import Color
from src.scenes.scenes import UIScene
from src.ui import *

class SimpleOverlayUI(UIScene):
    """
    Example UI that stays on top of the map
    """

    def __init__(self) -> None:
        super().__init__()
    
    def build(self) -> UIElement:
        return Center(
            content=Container(
                background_color=(6, 97, 153),
                border=Border(color=(255, 255, 255), width=2),
                width=100,
                height=100,
                content=Center(
                    content=Text('Overlay', color=(235, 239, 255), size=24, center=True)
                )
            )
        )