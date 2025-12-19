# simple-rpg

A simple rpg engine made in pygame with a lightweight clean architecture scaffold.

## Getting Started

1. Install dependencies (e.g., `pip install pygame`).
2. Run the game entry point:

```bash
python -m src.main
```

## Architecture

The project is structured to keep domain logic independent from Pygame:

- **domain**: Pure Python entities, scenes, and contracts that define how the game behaves.
- **application**: Coordination code such as the game loop and scene manager.
- **infrastructure**: Pygame adapters that implement the domain contracts for rendering, input, and timing.
- **assets** and **config**: Reserved directories for art/audio and configuration files.

This separation keeps the core logic testable and portable, while infrastructure can be swapped or extended as needed.
