"""Minimal intro menu example built on top of simple-rpg."""

from __future__ import annotations

from typing import Sequence

from src.game.domain.contracts import Color, InputEvent, Key, Renderer
from src.game.domain.scenes import Scene
from src.main import build_game


class IntroScene(Scene):
    """Intro UI showing common menu options."""

    background_color: Color = (12, 14, 28)

    def __init__(self) -> None:
        self._options = ["New Game", "Load Game", "Exit"]
        self._selected_index = 0
        self._subtitle = "Use ↑/↓ and Enter to choose an option."
        self._elapsed = 0.0

    def handle_events(self, events: Sequence[InputEvent]) -> None:
        for event in events:
            if event.type != "KEYDOWN" or event.payload is None:
                continue

            key = event.payload.get("key")
            if key == Key.UP:
                self._selected_index = (self._selected_index - 1) % len(self._options)
            elif key == Key.DOWN:
                self._selected_index = (self._selected_index + 1) % len(self._options)
            elif key == Key.ENTER:
                self._activate_option()

    def update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    def render(self, renderer: Renderer) -> None:
        renderer.clear(self.background_color)
        width, height = renderer.size

        renderer.draw_text("Simple RPG", (width // 2, height // 4), (235, 239, 255), 48, center=True)
        renderer.draw_text(self._subtitle, (width // 2, height // 4 + 48), (190, 198, 255), 24, center=True)

        start_y = height // 2 - (len(self._options) * 30)
        for index, option in enumerate(self._options):
            y = start_y + index * 60
            is_selected = index == self._selected_index

            if is_selected:
                pulse = (abs(((self._elapsed % 1.5) / 1.5) - 0.5) * 2)
                highlight = (
                    int(60 + 40 * pulse),
                    int(80 + 40 * pulse),
                    int(140 + 60 * pulse),
                )
                renderer.draw_rect(highlight, (width // 2 - 200, y - 10, 400, 50))

            renderer.draw_text(option, (width // 2, y), (240, 244, 255), 36, center=True)

    def _activate_option(self) -> None:
        choice = self._options[self._selected_index]
        if choice == "Exit":
            self.request_exit()
        else:
            self._subtitle = f"{choice} selected - swap in your own scene next!"


def main() -> None:
    game = build_game(title="Simple RPG Intro", initial_scene=IntroScene())
    game.run()


if __name__ == "__main__":
    main()
