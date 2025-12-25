"""Minimal intro menu example built on top of simple-rpg."""

from __future__ import annotations

from src.game.domain.contracts import Color
from src.game.domain.scenes import UIScene
from src.game.domain.ui_kit import *
from src.main import build_game


class IntroScene(UIScene):
    """Intro UI showing common menu options."""

    background_color: Color = (12, 14, 28)

    def __init__(self) -> None:
        super().__init__()
        self._options = ("New Game", "Load Game", "Exit")
        self._selected_index = 0
        self._subtitle = "Use ↑/↓ and Enter to choose an option."

    def build(self) -> UIElement:
        return Container(
            background_color=self.background_color,
            border=Border(color=(32, 40, 68), width=2),
            content=Column(
                contents=(
                    Spacing(48),
                    Text(
                        "Simple RPG",
                        color=(235, 239, 255),
                        size=48,
                        center=True,
                    ),
                    Text(
                        self._subtitle,
                        color=(190, 198, 255),
                        size=24,
                        center=True,
                    ),
                    Spacing(32),
                    Menu(
                        choices=(
                            MenuChoice(
                                "New Game",
                                value="new",
                                on_select=self._update_subtitle,
                                color=(240, 244, 255),
                                selected_color=(240, 244, 255),
                                highlight_color=(60, 80, 140),
                                size=36,
                                center=True,
                            ),
                            MenuChoice(
                                "Load Game",
                                value="load",
                                on_select=self._update_subtitle,
                                color=(240, 244, 255),
                                selected_color=(240, 244, 255),
                                highlight_color=(60, 80, 140),
                                size=36,
                                center=True,
                            ),
                            MenuChoice(
                                "Exit",
                                value="exit",
                                on_select=self._update_subtitle,
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
                    ),
                ),
                spacing=16,
            ),
        )

    def _update_subtitle(self, choice: MenuChoice) -> None:
        self._subtitle = f"{choice.label} selected - swap in your own scene next!"
        if choice.label in self._options:
            self._selected_index = self._options.index(choice.label)

    def _handle_choice(self, value: str | None) -> None:
        if value == "exit":
            self.request_exit()


def main() -> None:
    game = build_game(title="Simple RPG Intro", initial_scene=IntroScene())
    game.run()


if __name__ == "__main__":
    main()
