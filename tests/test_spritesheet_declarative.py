import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from src.game.domain.spritesheet_declarative import SpriteSheetAnimations


def test_animation_list_shorthand_converts_to_direction_map():
    animations = SpriteSheetAnimations(
        actions={
            "idle": [2, 5, 8, 11],
            "walk": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
                [10, 11, 12],
            ],
        }
    )

    normalized = animations.to_animation_map(
        sheet_size=(4, 4),
        one_indexed=True,
    )

    assert normalized == {
        "idle": {
            "down": [1],
            "left": [4],
            "right": [7],
            "up": [10],
        },
        "walk": {
            "down": [0, 1, 2],
            "left": [3, 4, 5],
            "right": [6, 7, 8],
            "up": [9, 10, 11],
        },
    }


def test_out_of_range_ids_raise_error():
    animations = SpriteSheetAnimations(actions={"idle": [1, 2, 3, 10]})

    with pytest.raises(ValueError, match="must be between"):
        animations.to_animation_map(sheet_size=(3, 3), one_indexed=True)
