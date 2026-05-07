# First Implementation Tasks

## Phase 1: Pygame setup

### Goal

Open a working game window with a stable loop and central configuration.

### Tasks

1. Create `requirements.txt` with `pygame` and `pytest`.
2. Create `main.py`.
3. Initialize Pygame and create a window sized for:
   - map: `26 x 26`
   - tile size: `24px`
   - map area: `624 x 624`
   - extra width or height for HUD
4. Add a basic loop with:
   - event handling
   - quit handling
   - fixed FPS clock
   - screen clear
   - display update
5. Create `config/settings.py` for:
   - tile size
   - grid width and height
   - screen width and height
   - FPS
   - colors

### Done when

- The window opens reliably
- The loop runs at a fixed FPS
- The app exits cleanly without hanging

## Phase 2: Tile system foundation

### Goal

Represent and draw the game arena as a proper tile map before adding tanks.

### Tasks

1. Create `game/world/tiles.py`.
2. Define:
   - tile type enum
   - whether each tile blocks tanks
   - whether each tile blocks bullets
   - whether each tile is destructible
3. Create `game/world/map_loader.py`.
4. Add one hardcoded starter level as a `26 x 26` matrix.
5. Create a `TileMap` structure that stores:
   - width
   - height
   - tile grid
   - player spawn
   - enemy spawns
   - eagle position
6. Create `game/ui/renderer.py` logic to draw each tile type in a different color first.
7. Verify tile-to-pixel conversion:
   - `pixel_x = tile_x * TILE_SIZE`
   - `pixel_y = tile_y * TILE_SIZE`
8. Render the full map and confirm visual scale is acceptable.

### Done when

- A `26 x 26` tile arena is visible
- Different tile types render distinctly
- The eagle and spawn points are placed consistently
- The tile system can be reused later by collision and AI modules

## Phase 3: Early technical guardrails

### Tasks

1. Keep map logic free from direct Pygame dependencies except drawing code.
2. Store level data separately from rendering code.
3. Use constants from `config/settings.py`, not hardcoded numbers.
4. Write one early test for:
   - tile blocking rules
   - map dimensions
   - eagle position validity

## Mistakes to avoid immediately

- Do not start with sprites before the tile system works.
- Do not mix pixel movement rules into tile definitions.
- Do not hardcode screen math in multiple places.
- Do not let `main.py` become the home for all logic.
