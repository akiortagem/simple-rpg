# Running the Game Loop

The `GameLoop` class in `src/game/application/game_loop.py` coordinates event polling, scene updates, rendering, and presentation.

```python
from src.main import build_game
from src.game.domain.scenes import DemoScene

game = build_game(initial_scene=DemoScene())
game.run()
```

## What the loop does

Each iteration of `GameLoop.run`:

1. Polls events from the configured `EventSource` (pygame in the default build) and forwards them to the `SceneManager`.
2. Checks whether the current scene requested exit or if a `QUIT` event arrived.
3. Ticks the `TimeSource` to compute `delta_time`.
4. Calls `update` on the active scene.
5. Calls `render` on the active scene with the renderer, then `present` to swap the frame.

`SceneManager` is responsible for invoking `on_enter`/`on_exit` when scenes change and routing `handle_events`, `update`, and `render` to the active scene.

## Integrating your own scenes

- Use `build_game` for a pygame-powered setup, or construct `GameLoop` manually with your own `Renderer`, `EventSource`, `TimeSource`, and `SceneManager` if you need to swap infrastructure.
- Scenes must implement `update` and `render`. In tilemap scenes, `MapScene` already wires input handling, collision checks, and sprite rendering for you.

When you're ready to quit (for example, in response to menu input), call `request_exit()` on the scene so the loop ends after the current frame.
