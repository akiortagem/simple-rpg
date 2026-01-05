# Setup

Follow these steps to install dependencies and prepare a project that uses Simple RPG.

## Install dependencies

1. Ensure you have Python 3.11+ installed.
2. Install [pygame](https://www.pygame.org/) and any other dependencies your project requires:
   ```bash
   pip install pygame
   ```

## Basic bootstrap

`src/main.py` exposes a `build_game` helper that wires up the pygame-based renderer, event source, and clock with a scene manager and the central `GameLoop` class. Import your own scene and pass it as `initial_scene`:

```python
from src.main import build_game
from src.scenes.scenes import Scene

class MyScene(Scene):
    def update(self, delta_time: float) -> None:
        ...

    def render(self, renderer) -> None:
        ...

game = build_game(width=800, height=600, title="My RPG", initial_scene=MyScene())
game.run()
```

`build_game` creates a pygame window, constructs a `SceneManager`, and returns a `GameLoop` instance ready to run the loop. When you call `game.run()`, the loop polls events, updates the scene, renders, and presents the frame.
