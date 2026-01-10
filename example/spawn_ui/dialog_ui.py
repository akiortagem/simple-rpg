from __future__ import annotations

from src.core.contracts import Color
from src.scenes.scenes import UIScene
from src.ui import *

class DialogUI(UIScene):
    """
    Example UI that gets spawned on event. This is a dialog example
    """

    def __init__(self, dialog_text:str) -> None:
        super().__init__()
        self.dialog_text = dialog_text
    
    def build(self) -> UIElement:
        return KeypressDetector(
            on_interact=lambda: self.pop(), # when player presses the interact button, it despawns itself
            content=Positioned(
                bottom=100, # pixels from bottom of the parent UIElement
                # top=999, # pixels from top
                # left=999, # pixels from left
                # right=999, # pixels from right
                content=Container(
                    background_color=(6, 97, 153),
                    border=Border(color=(255, 255, 255), width=2),
                    width=100,
                    height=100,
                    content=Center(
                        content=Text(self.dialog_text, color=(235, 239, 255), size=24)
                    )
                )
            )
        )