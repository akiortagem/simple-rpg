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
from src.io.tilemap_parser import parse_tilemap

visual_tiles = parse_tilemap(
    tilemap=\"\"\"
    1 1 2 2
    1 3 3 2
    \"\"\"
)

collision_tiles = parse_tilemap(tilemap_file=\"assets/collision_map.txt\", collision=True)
```

## Credits

### body/bodies/male/walk/light.png
see details at https://opengameart.org/content/lpc-character-bases; 'Thick' Male Revised Run/Climb by JaidynReiman (based on ElizaWy's LPC Revised)

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: bluecarrot16, JaidynReiman, Benjamin K. Smith (BenCreating), Evert, Eliza Wyatt (ElizaWy), TheraHedwig, MuffinElZangano, Durrani, Johannes Sjölund (wulax), Stephen Challener (Redshrike)

### head/heads/human/male/walk/light.png
original head by Redshrike, tweaks by BenCreating, modular version by bluecarrot16

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: bluecarrot16, Benjamin K. Smith (BenCreating), Stephen Challener (Redshrike)

### head/faces/male/neutral/walk/light.png
Original by Redshrike, Expressions by ElizaWy, mapped to all frames by JaidynReiman

Licenses: OGA-BY 3.0

Authors: JaidynReiman, ElizaWy, Stephen Challener (Redshrike)

### hair/spiked_porcupine/adult/walk/raven.png
Licenses: CC-BY-SA 3.0

Authors: Fabzy, bluecarrot16

### torso/armour/plate/male/walk/steel.png
original by wulax, recolor by bigbeargames, color reduced to 7 colors and adapted to v3 bases by bluecarrot16, run/jump/sit/climb/revised combat by JaidynReiman

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: JaidynReiman, bluecarrot16, Michael Whitlock (bigbeargames), Johannes Sjölund (wulax)

### cape/trim/female/walk/black.png
isolated stripe from cape_trimmed, adapted to v3 bases by bluecarrot16

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: bluecarrot16, JaidynReiman

### cape/tattered/female/walk/bluegray.png
Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: Nila122, JaidynReiman

### cape/tattered_behind/walk/bluegray.png
Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: Nila122, JaidynReiman

### legs/cuffed/male/walk/leather.png
Original bases by Redshrike, thrust/shoot bases by Wulax, original overalls by ElizaWy, base animations adapted from v3 overalls by bluecarrot16, pants by JaidynReiman

Licenses: OGA-BY 3.0, GPL 3.0

Authors: JaidynReiman, ElizaWy, Bluecarrot16, Johannes Sjölund (wulax), Stephen Challener (Redshrike)

### feet/boots/fold/male/walk/black.png
Licenses: OGA-BY 3.0+, CC-BY 3.0+, GPL 3.0

Authors: JaidynReiman

### bauldron/male/walk/brown.png
Licenses: GPL 2.0, GPL 3.0, OGA-BY 3.0, CC-BY-SA 3.0

Authors: Nila122

### shoulders/plate/male/walk/steel.png
recolors, adapted to v3 bases by bluecarrot16

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: bluecarrot16, Johannes Sjölund (wulax)

### arms/armour/plate/male/walk/steel.png
original by wulax, recolors by bigbeargames; adapted to v3 bases and further recolors by bluecarrot16

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: Michael Whitlock (bigbeargames), Matthew Krohn (makrohn), Johannes Sjölund (wulax)

### arms/gloves/male/walk/brass.png
metal gloves by wulax, recolors by bigbeargames, adapted to v3 bases by bluecarrot16, added to expanded animations by JaidynReiman

Licenses: OGA-BY 3.0, CC-BY-SA 3.0, GPL 3.0

Authors: Michael Whitlock (bigbeargames), Matthew Krohn (makrohn), Johannes Sjölund (wulax), bluecarrot16, JaidynReiman
