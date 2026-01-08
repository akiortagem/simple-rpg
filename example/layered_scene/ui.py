from __future__ import annotations

from src.core.contracts import Color
from src.scenes.scenes import UIScene
from src.ui import *

class SimpleOverlayUI(UIScene):
    """
    Example UI that stays on top of the map
    """

    background_color: Color = (12, 14, 28)

    def __init__(self) -> None:
        super().__init__()
    
    def build(self) -> UIElement:
        return Center(
            content=Container(
                background_color=self.background_color,
                border=Border(color=(32, 40, 68), width=2),
                width=100,
                height=100,
                content=Text('Overlay', color=(235, 239, 255), size=24, center=True)
            )
        )