# simple-rpg

A simple rpg engine made in pygame with a lightweight clean architecture scaffold.

## Getting Started

1. Install dependencies (e.g., `pip install pygame`).
2. Import the `build_game` helper and provide your own scenes to start a loop:

```python
from src.main import build_game
from src.scenes.scenes import Scene

class MyScene(Scene):
    ...

game = build_game(initial_scene=MyScene())
game.run()
```

An example intro menu is available in [`example/intro_ui`](example/intro_ui). Run it with `python -m example.intro_ui.main` to see how to compose scenes and bootstrap the loop.

## Documentation

New to the engine? Start with the guides in [`docs/`](docs/index.md) for setup, tilemap scenes, sprites, tilesets, and running the game loop.

## Architecture

The project is structured to keep domain logic independent from Pygame:

- **domain**: Pure Python entities, scenes, and contracts that define how the game behaves.
- **application**: Coordination code such as the game loop and scene manager.
- **infrastructure**: Pygame adapters that implement the domain contracts for rendering, input, and timing.
- **assets** and **config**: Reserved directories for art/audio and configuration files.

This separation keeps the core logic testable and portable, while infrastructure can be swapped or extended as needed.
