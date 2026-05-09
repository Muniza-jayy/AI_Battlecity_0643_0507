"""Fixed level data for the initial playable map."""

from __future__ import annotations

from typing import Final

from config.settings import GRID_HEIGHT, GRID_WIDTH


STARTER_LEVEL_LAYOUT: Final[list[str]] = [
    "....................BBBBB.",
    ".BBB.WW..SSS...WW...BBB...",
    ".BBB.WW..SSS...WW...BBB...",
    "...W..BBB..WW..BBB..SSS...",
    "...W..BBB..WW..BBB..SSS...",
    "..WW....BBB.SSS.BBB...WW..",
    "..WW....BBB.SSS.BBB...WW..",
    "....FFF....SSS....FFF.....",
    "....FFF....SSS....FFF.....",
    "..BBB....WWWW....SSS......",
    "..BBB....WWWW....SSS......",
    "..........WW..............",
    "..........................",
    "..FFF..............FFF....",
    "..FFF...BBB....SSS.FFF....",
    "........BBB....SSS........",
    "..WW....BBB....SSS....WW..",
    "..WW.................WW...",
    "......SSS....BBB..........",
    "......SSS....BBB....FFF...",
    "......WW.....BBB....FFF...",
    "..BBB.WW.....SSS....FFF...",
    ".P......................P.",
    ".........BBB.E.BBB........",
    "..........BB...BB.........",
    "............P.............",
]

PLAYER_SPAWN: Final[tuple[int, int]] = (12, 25)
ENEMY_SPAWNS: Final[tuple[tuple[int, int], ...]] = ((0, 0), (12, 0), (25, 0))
EAGLE_POSITION: Final[tuple[int, int]] = (13, 23)
STARTER_ENEMY_POOL: Final[tuple[str, ...]] = (
    "basic",
    "basic",
    "fast",
    "fast",
    "armor",
    "armor",
)

STEEL_FORTRESS_LAYOUT: Final[list[str]] = [
    row.replace("B", "S")
    for row in STARTER_LEVEL_LAYOUT
]

STEEL_FORTRESS_PLAYER_SPAWN: Final[tuple[int, int]] = PLAYER_SPAWN
STEEL_FORTRESS_ENEMY_SPAWNS: Final[tuple[tuple[int, int], ...]] = ENEMY_SPAWNS
STEEL_FORTRESS_EAGLE_POSITION: Final[tuple[int, int]] = EAGLE_POSITION
STEEL_FORTRESS_ENEMY_POOL: Final[tuple[str, ...]] = (
    "basic",
    "fast",
    "fast",
    "armor",
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
assert len(STEEL_FORTRESS_LAYOUT) == GRID_HEIGHT
assert all(len(row) == GRID_WIDTH for row in STEEL_FORTRESS_LAYOUT)
