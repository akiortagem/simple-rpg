from .map import SimpleMapScene
from .ui import SimpleOverlayUI
from src.scenes.scenes import LayeredScene
from src.main import build_game

def main() -> None:
    scene = LayeredScene( # This scene draws layers of each scenes passed into it
        scenes=[
            # From top to bottom layer
            SimpleOverlayUI(),
            SimpleMapScene(),
        ]
    )
    game = build_game(title="Simple RPG - Simple Layered Scene", initial_scene=scene, debug_collision=True)
    game.run()


if __name__ == "__main__":
    main()
