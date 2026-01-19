from __future__ import annotations

from src.scenes.scenes import UIScene
from src.scenes.utils import to_scene
from src.ui import *

from .intro_scene import IntroScene

class PauseGameMenuDialog(UIScene):
    """
    Example UI that shows up on pause
    """

    def __init__(self) -> None:
        super().__init__()
        self._selected_index = 0
    
    def _handle_choice(self, value: str | None) -> None:
        if value == "resume":
            self.pop()
        if value == "exit":
            to_scene(IntroScene())
    
    def build(self) -> UIElement:
        return Center(
                content=Container( # No width and height passed means that the container should expand to fit its content
                    background_color=(6, 97, 153),
                    border=Border(color=(255, 255, 255), width=2),
                    content=Center(
                        content=Menu(
                        choices=(
                                MenuChoice(
                                    "Resume Game",
                                    value="resume",
                                    color=(240, 244, 255),
                                    selected_color=(240, 244, 255),
                                    highlight_color=(60, 80, 140),
                                    size=36,
                                    center=True,
                                ),
                                MenuChoice(
                                    "Exit",
                                    value="exit",
                                    color=(240, 244, 255),
                                    selected_color=(240, 244, 255),
                                    highlight_color=(60, 80, 140),
                                    size=36,
                                    center=True,
                                ),
                            ),
                            spacing=12,
                            selected_index=self._selected_index,
                            on_choose=self._handle_choice,
                        )
                    )
                )
            )