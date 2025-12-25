# Map Scenes and Tilemaps

The `MapScene` class orchestrates tile layers, collision detection, and characters. Provide at least one renderable tilemap and a player sprite; optional NPC controllers can join the scene.

```python
from src.game.domain.scenes import MapScene
from src.game.domain.tilemap_layer import TilemapLayer, TilesetDescriptor
from src.game.domain.tilemap import Tilemap, TileCollisionDetector
from src.game.domain.sprites import PCMapSprite, SpriteSheetDescriptor
```

## Visual and collision layers

`MapScene` expects two tilemap-like collaborators:

- `visual_tilemap`: Any object implementing the `RenderableTilemapLayer` protocol. `TilemapLayer` is a ready-made option that knows how to draw a grid of tile IDs from a tileset image. When rendered, it uses the renderer's size and camera offset to only draw visible tiles.
- `collision_tilemap`: Either a `CollisionDetector` (for hit tests) or another `RenderableTilemapLayer` (for rendering). Using `TileCollisionDetector` with a `Tilemap` lets you mark impassable tile IDs and share the same sizing metadata that sprites need for bounds clamping.

The scene computes map bounds from either `pixel_size` or `size` on these collaborators, and assigns them to every sprite so they can clamp movement and avoid walking off the map.

### Building a tileset and layer

```python
# Slice a sprite sheet image into fixed-size tiles.
tileset = TilesetDescriptor(
    image="assets/tileset.png",
    tile_width=16,
    tile_height=16,
    columns=8,
)

# Rows of tile IDs that reference the tileset grid; None entries skip drawing.
tile_rows = [
    [0, 1, 1, 2],
    [8, 9, 9, 10],
]

visual_layer = TilemapLayer(tileset=tileset, tiles=tile_rows)
```

### Blocking movement with a collision map

```python
collision_map = Tilemap(
    tiles=tile_rows,  # You can share the same layout or load a separate collision-only grid
    tile_size=(tileset.tile_width, tileset.tile_height),
    impassable_ids={1, 9},
)
collision_detector = TileCollisionDetector(tilemap=collision_map)
```

Pass both objects to `MapScene`, plus your player sprite (and optional NPC controllers):

```python
scene = MapScene(
    visual_tilemap=visual_layer,
    collision_tilemap=collision_detector,
    player=my_player,
    npc_controllers=[guard_controller, shopkeeper_controller],
)
```

`MapScene` will route input to the player, update all sprites and controllers, and render the tilemap followed by every sprite each frame.

## Camera and scrolling

`MapScene` keeps a camera that follows the player's hitbox and clamps itself to the map bounds before rendering. The renderer's size determines how much of the map is visible at once, so the viewport stays fixed while the tilemap and sprites scroll underneath. Developers can pan the view without dealing with renderer math by calling `scene.pan_camera(dx, dy)` or apply a sequence of moves at once with `scene.pan_camera_route([(dx, dy), ...])`; the offset persists across frames and stacks with the automatic player tracking.
