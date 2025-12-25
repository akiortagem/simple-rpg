# Sprites and Tilesets

Sprites and tilesets describe how to slice images so the renderer can draw frames and tiles.

## Character sprites

`CharacterSprite` and its map-aware subclasses (`PCMapSprite`, `NPCMapSprite`) use `SpriteSheetDescriptor` to describe a spritesheet grid:

```python
from src.game.domain.sprites import PCMapSprite, SpriteSheetDescriptor

player_sheet = SpriteSheetDescriptor(
    image="assets/player.png",
    frame_width=32,
    frame_height=32,
    columns=4,
    animations={
        "idle": {"down": [0]},
        "walk": {
            "down": [0, 1, 2, 3],
            "left": [4, 5, 6, 7],
            "right": [8, 9, 10, 11],
            "up": [12, 13, 14, 15],
        },
    },
)

player = PCMapSprite(x=100, y=100, spritesheet=player_sheet, speed=150)
```

`PCMapSprite` handles keyboard input and sets velocity based on `Key` names. The base `CharacterMapSprite` class clamps movement to `map_bounds`, checks collisions via `CollisionDetector`, advances animations, and exposes a `hitbox` property that factors in the frame dimensions.

## Tilesets for tilemaps

`TilesetDescriptor` describes a tileset image for `TilemapLayer` to render:

```python
from src.game.domain.tilemap_layer import TilesetDescriptor

tileset = TilesetDescriptor(
    image="assets/tileset.png",
    tile_width=16,
    tile_height=16,
    columns=8,
)
```

`TilemapLayer` accepts a 2D sequence of tile IDs. Each ID references a tile in the tileset grid (row-major order), while `None` or negative values skip drawing. Provide optional `tile_offsets` with per-cell `(dx, dy)` tuples to nudge placements, useful for tall tiles like trees.
