# Simple RPG Developer API

This document summarizes the public, developer-facing modules exposed under
`src/`, along with key types and usage patterns.

## Engine setup

### Quick start

Use `build_game` to wire pygame adapters with the engine and start the loop:

```python
from src.main import build_game
from src.scenes import DemoScene

loop = build_game(title="Simple RPG", initial_scene=DemoScene())
loop.run()
```

### Manual wiring

If you want to assemble the pieces yourself, use the engine contracts directly:

```python
from src.core import GameConfig
from src.engine import GameLoop, SceneManager
from src.io import PygameClock, PygameEventSource, PygameRenderer
from src.scenes import Scene

class MyScene(Scene):
    def update(self, delta_time: float) -> None:
        ...

    def render(self, renderer) -> None:
        ...

scene_manager = SceneManager(initial_scene=MyScene(), config=GameConfig())
renderer = PygameRenderer((800, 600), "Simple RPG")
events = PygameEventSource()
clock = PygameClock()

loop = GameLoop(scene_manager=scene_manager, renderer=renderer, events=events, clock=clock)
loop.run()
```

## Modules and key entry points

### `src.core`

Core contracts and entities:

- `Renderer`, `EventSource`, `TimeSource` protocols in `src.core.contracts`.
- `InputEvent`, `Key`, and `GameConfig` for framework-agnostic input and config.
- `Entity` in `src.core.entities` for lightweight positioned objects.

### `src.engine`

Game loop orchestration:

- `SceneManager` (`src.engine.scene_manager`) owns the current scene and calls
  `Scene.on_enter`, `Scene.on_exit`, `Scene.handle_events`, `Scene.update`, and
  `Scene.render`.
- `GameLoop` (`src.engine.game_loop`) drives the loop via `GameLoop.run`.

### `src.scenes`

Scene abstractions and built-in scene types:

- `Scene` base class with `request_exit`, `handle_events`, `update`, and `render`.
- `UIScene` for UI-driven screens that pair with `UIController` and `UIRenderer`.
- `MapScene` and `MapSceneBase` for tilemap-based gameplay.
- `DemoScene` for quick scaffolding and examples.

### `src.world`

World building and sprites:

- Declarative map definitions in `src.world.map_scene_declarative`:
  `Map`, `MapPC`, `MapNPC`, `TileSheet`, and `build_map_scene_assets`.
- Sprite handling in `src.world.sprites`:
  `CharacterSprite`, `PCMapSprite`, `NPCMapSprite`, `CollisionDetector`, and
  `SpriteSheetDescriptor` alongside `normalize_animation_map`.
- Tilemap rendering in `src.world.tilemap` and `src.world.tilemap_layer`:
  `Tilemap`, `TileCollisionDetector`, `TilemapLayer`, and `TilesetDescriptor`.
- NPC behavior in `src.world.npc_controller` and `src.world.npc_routes`:
  `NPCController`, `NPCMapController`, and route definitions like `LoopRoute`.

### `src.ui`

Declarative UI system:

- Layout primitives: `Size`, `Rect`, `LayoutNode`, `UIElement` in `src.ui.base`.
- Components: `Column`, `Container`, `Border`, `Text`, `Menu`, `MenuChoice`,
  `Spacing`, and `Dialog`.
- `UIController` (`src.ui.controller`) for focus and input handling.

### `src.io`

Infrastructure adapters and IO helpers:

- `PygameRenderer`, `PygameEventSource`, and `PygameClock` in
  `src.io.pygame_adapter` implement `Renderer`, `EventSource`, and `TimeSource`.
- `load_image` in `src.io.assets` for sprite and tileset image loading.
- `parse_tilemap` in `src.io.tilemap_parser` for text-based tilemaps.

### `src.util`

Path utilities:

- `resolve_asset`, `resolve_config`, and directory constants in `src.util.paths`
  for locating project assets and config files.
