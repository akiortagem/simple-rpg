# Simple Map Example

This example builds a 10x10 overworld using the declarative map scene API. It includes a
patrolling NPC, an idle NPC, and a controllable player character.

## Running

From the repository root:

```bash
python -m example.simple_map.main
```

## Tilemap parsing helpers

Use `parse_tilemap` to turn a multiline string or file into a 2D grid. Visual tilemaps accept 1-based IDs that are converted to 0-based indices automatically, while collision grids can keep `0/1` values intact.

```python
from src.game.domain.tilemap_parser import parse_tilemap

visual_tiles = parse_tilemap(
    tilemap=\"\"\"
    1 1 2 2
    1 3 3 2
    \"\"\"
)

collision_tiles = parse_tilemap(tilemap_file=\"assets/collision_map.txt\", collision=True)