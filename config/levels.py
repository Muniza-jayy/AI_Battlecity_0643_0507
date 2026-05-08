"""Fixed level data for the initial playable map."""

from __future__ import annotations

from typing import Final

from config.settings import GRID_HEIGHT, GRID_WIDTH


STARTER_LEVEL_LAYOUT: Final[list[str]] = [
    "..........................",
    ".B...W....S.....W....B...B",
    "..S.....B.....S.....B....W",
    "...W..B....W....B....S....",
    ".B....S.....B......W....B.",
    "..W....B....S....B.....W..",
    "....S.....W....B.....S....",
    ".B....W.....S.....B....W..",
    "..B.....S....W....B.....S.",
    "....W....B.....S.....W....",
    ".S.....B....W....S.....B..",
    "..W....S.....B.....W....S.",
    "..........................",
    "...F.....F......F.....F...",
    "....B....W....S.....B.....",
    "..S.....B.....W....S....B.",
    ".W....B....S.....B.....W..",
    "....S.....B....W.....S....",
    "..B....W.....S....B.....W.",
    ".S.....B....W.....S....B..",
    "......W.....B....S.....W..",
    "..B.....S....W.....B....S.",
    ".P......................P.",
    "..........BBS.E.SBB.......",
    "...........BB...BB........",
    "............P.............",
]

PLAYER_SPAWN: Final[tuple[int, int]] = (12, 25)
ENEMY_SPAWNS: Final[tuple[tuple[int, int], ...]] = ((0, 0), (12, 0), (25, 0))
EAGLE_POSITION: Final[tuple[int, int]] = (14, 23)
STARTER_ENEMY_POOL: Final[tuple[str, ...]] = (
    "basic",
    "basic",
    "fast",
    "fast",
    "armor",
    "armor",
)

BOSS_LEVEL_LAYOUT: Final[list[str]] = [
    "............",
    "..B....S....",
    "....W....B..",
    "...S.....W..",
    "............",
    ".F....B.....",
    ".....B......",
    "..W.....S...",
    "....S....W..",
    ".....B......",
    "....BESB....",
    ".....P......",
]

BOSS_PLAYER_SPAWN: Final[tuple[int, int]] = (5, 11)
BOSS_ENEMY_SPAWNS: Final[tuple[tuple[int, int], ...]] = ((5, 0),)
BOSS_EAGLE_POSITION: Final[tuple[int, int]] = (5, 10)
BOSS_ENEMY_POOL: Final[tuple[str, ...]] = ("boss",)


assert len(STARTER_LEVEL_LAYOUT) == GRID_HEIGHT
assert all(len(row) == GRID_WIDTH for row in STARTER_LEVEL_LAYOUT)
