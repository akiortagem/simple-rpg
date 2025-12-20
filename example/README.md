# Example projects

This directory contains reference projects that use the simple-rpg framework.
They are intentionally lightweight and meant to be copied into your own project layout.

- `intro_ui`: A minimal intro menu with "New Game", "Load Game", and "Exit" options built on top of the provided scene and game loop abstractions.
- `simple_map`: A 50x50 overworld with a controllable player, a patrolling NPC that walks a square route, and a stationary NPC. It highlights tilemap rendering, collision handling, and basic NPC routing.

## Running the intro UI example

From the repository root, install the project dependencies (e.g., `pip install -e .`) and run:

```bash
python -m example.intro_ui.main
```

## Running the simple map example

Add the expected image assets under `example/simple_map/assets` (see the comment header in `example/simple_map/main.py` for the filenames). Then run:

```bash
python -m example.simple_map.main
```
