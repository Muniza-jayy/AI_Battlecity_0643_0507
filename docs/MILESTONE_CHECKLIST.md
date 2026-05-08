# Milestone Checklist

## Milestone 1: Project bootstrap

- [ ] Create project folders and `__init__.py` files where needed
- [ ] Add `requirements.txt`
- [ ] Add `main.py` with a minimal Pygame window
- [ ] Add `config/settings.py` with screen, tile, and FPS constants
- [ ] Confirm the game opens and closes cleanly

## Milestone 2: Tile map foundation

- [ ] Define tile types: empty, brick, steel, water, forest, eagle
- [ ] Implement `TileMap` data structure
- [ ] Add fixed `26 x 26` level data for one standard level
- [ ] Render the grid and tiles on screen
- [ ] Verify `24px` tile size gives a readable arena

## Milestone 3: Core gameplay loop

- [ ] Build fixed-timestep update loop
- [ ] Add `GameState`
- [ ] Separate input, update, and render phases
- [ ] Add pause/quit handling

## Milestone 4: Player movement and collision

- [ ] Add player tank entity
- [ ] Implement four-direction movement
- [ ] Enforce solid collision against blocking tiles
- [ ] Add alignment assist for turning near tile centers
- [ ] Prevent overlap with the eagle

## Milestone 5: Projectiles and destruction

- [ ] Add bullet entity
- [ ] Limit each tank to one active bullet at a time
- [ ] Implement swept-path bullet movement
- [ ] Destroy bricks on hit
- [ ] Block bullets with steel
- [ ] Apply damage to tanks and eagle

## Milestone 6: Match rules

- [ ] Add lives, score, and eagle state
- [ ] Add lose conditions
- [ ] Add win condition for clearing all enemies
- [ ] Add HUD

## Milestone 7: Enemy AI foundation

- [ ] Add enemy spawn points
- [ ] Implement Basic Tank with BFS
- [ ] Add decision tick timing
- [ ] Add line-of-sight shooting
- [ ] Verify enemy behavior is visible and understandable

## Milestone 8: AI variety

- [ ] Add Fast Tank with Greedy Best-First Search
- [ ] Add Armor Tank with A*
- [ ] Support dynamic replanning after map changes
- [ ] Tune speeds and decision intervals

## Milestone 9: Boss level

- [ ] Add `12 x 12` boss arena
- [ ] Add Boss Tank state and phases
- [ ] Implement Minimax with alpha-beta pruning
- [ ] Track node counts and pruning metrics

## Milestone 10: CSP map generator and debug tools

- [ ] Implement CSP-based random map generation
- [ ] Enforce eagle protection and spawn-to-eagle reachability
- [ ] Add simulation/debug mode
- [ ] Add optional debug overlay for paths and AI labels
- [ ] Add automated tests for collision, pathfinding, and map validity

## UI/UX Phase

### UI Milestone 1: App screen system

- [x] Add app-level screen enum/state
- [x] Separate `WELCOME`, `OPTIONS`, `ABOUT`, `PLAYING`, `PAUSED`, `GAME_OVER`
- [x] Move screen routing out of `main.py`
- [x] Keep gameplay loop reusable under `PLAYING`

### UI Milestone 2: Welcome screen

- [x] Build landing screen for `Battle City AI`
- [x] Add subtitle: `CSP | BFS | Greedy | A* | Minimax`
- [x] Add animated cyber/grid background
- [x] Add buttons:
- [x] `Start Game`
- [x] `Game Options`
- [x] `About Project`
- [x] `Quit`

### UI Milestone 3: Options screen

- [ ] Add level selection:
- [ ] `Level 1: Brick Maze`
- [ ] `Level 2: Steel Fortress`
- [ ] `Boss Arena`
- [ ] Add debug overlay toggle
- [ ] Add path visualization toggle
- [ ] Add difficulty selection:
- [ ] `Easy`
- [ ] `Normal`
- [ ] `Hard`
- [ ] Add back button

### UI Milestone 4: About screen

- [ ] Add AI Lab project summary
- [ ] Add tank-to-algorithm mapping
- [ ] Add back button
- [ ] Polish presentation panel styling

### UI Milestone 5: Playing / pause / game-over UX

- [ ] Add proper pause overlay
- [ ] Add styled game-over / victory states
- [ ] Add screen transitions between gameplay and UI states
- [ ] Preserve existing game logic under screen routing

### UI Milestone 6: Visual polish pass

- [ ] Tune typography hierarchy
- [ ] Unify neon palette and panel language
- [ ] Improve hover/press feedback
- [ ] Refine animation timing
- [ ] Clean up resize/layout behavior
