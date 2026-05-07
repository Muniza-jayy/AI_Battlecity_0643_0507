# Architecture Plan

## Final decisions

- The product is a human-playable game first, with simulation/debug support as a secondary capability.
- Gameplay stays real-time and visually readable; AI must be visible through movement and firing choices, not hidden metrics alone.
- The arena remains tile-based, but tanks and bullets move continuously in pixel space.
- Collision is strict: tanks do not overlap walls, the eagle, or each other.
- Turning is assisted only enough to feel responsive; movement must not devolve into ghosting through corners.
- Bullets are visible projectiles with swept-path hit detection.
- Enemy behavior is differentiated by algorithm and role: BFS for Basic Tanks, Greedy for Fast Tanks, A* for Armor Tanks, Minimax with alpha-beta pruning for the Boss Tank.
- The CSP map generator is constrained by playability rules rather than being purely random.
- The primary loop is a playable match; simulation mode reuses the same rules instead of forking the game logic.

## System shape

Build the project as a small set of cooperating modules around a single canonical game state. Keep rendering, rules, and AI separate so that the same mechanics can drive normal play, debugging, and evaluation.

## Module plan

### 1. `config/`

Purpose: centralize constants so arena size, speeds, hit points, decision intervals, and level settings are not scattered through gameplay code.

Key contents:
- `settings.py`: screen size, tile size, tick rate, colors, asset paths
- `balance.py`: tank speeds, bullet speeds, HP, spawn cadence, AI decision intervals
- `levels.py`: fixed level metadata and boss-phase depth settings

### 2. `core/`

Purpose: own the deterministic game model and update loop.

Key contents:
- `state.py`: dataclasses for game state, tanks, bullets, tile map, eagle, lives, score, and active wave
- `loop.py`: top-level tick order
- `events.py`: lightweight domain events such as `bullet_fired`, `tank_destroyed`, `eagle_hit`, `wave_spawned`
- `timers.py`: cooldowns, decision timers, spawn timers, boss phase transitions

Update order per tick:
1. Read player input
2. Trigger enemy AI decisions whose `Decision Tick` has elapsed
3. Apply movement intents
4. Spawn bullets from accepted fire intents
5. Advance projectiles with swept collision checks
6. Resolve destruction, score, and map changes
7. Spawn new enemies if the wave allows it
8. Evaluate win/lose conditions

### 3. `world/`

Purpose: represent levels and enforce spatial rules.

Key contents:
- `tiles.py`: tile types, movement blocking rules, bullet interaction rules
- `map_loader.py`: load fixed level layouts from simple arrays or JSON
- `map_generator.py`: CSP-based random map generation using backtracking, forward checking, and BFS validation
- `collision.py`: wall, tank, eagle, and projectile collision helpers
- `alignment.py`: lane-snapping logic for responsive turning without overlap

Rules to encode:
- Brick blocks tanks and can be destroyed by bullets
- Steel blocks tanks and bullets
- Water blocks tanks
- Forest preserves readability rules without changing collision unless explicitly designed otherwise
- Spawn-to-eagle reachability is mandatory for generated maps

### 4. `entities/`

Purpose: implement behavior shared by player and enemies without baking AI into rendering code.

Key contents:
- `tank.py`: movement, facing, cooldowns, hit handling
- `player.py`: input-driven intent generation
- `enemy.py`: AI-driven intent generation shell
- `bullet.py`: projectile movement and impact behavior

Important boundary:
- Entities produce intents such as `move_up` or `fire`
- The `core` and `world` layers decide whether those intents become legal state transitions

### 5. `ai/`

Purpose: isolate algorithm implementations from the rest of the game rules.

Key contents:
- `graph.py`: grid graph extraction from the current tile map
- `heuristics.py`: Manhattan distance and terrain-aware path costs
- `bfs_agent.py`: Basic Tank planner
- `greedy_agent.py`: Fast Tank planner
- `astar_agent.py`: Armor Tank planner
- `minimax_agent.py`: Boss Tank planner with alpha-beta pruning
- `line_of_sight.py`: shared shot-opportunity checks
- `evaluation.py`: boss evaluation function and pruning metrics

Design rules:
- AI reads a snapshot of the current game state and returns intents, not direct mutations
- Replanning happens only on decision ticks or when the current plan becomes invalid
- Pathfinding should work on tile centers, while movement execution remains continuous

### 6. `modes/`

Purpose: keep player-facing play and debug/simulation flows thin and reusable.

Key contents:
- `play_mode.py`: normal game session orchestration
- `simulation_mode.py`: scripted or autoplay inspections using the same state transitions
- `level_flow.py`: level progression, wave setup, and boss-stage transitions

Rule:
- No duplicate game rules here; these modules compose `core`, `world`, `entities`, and `ai`

### 7. `ui/`

Purpose: render the game clearly and expose enough information to understand AI behavior.

Key contents:
- `renderer.py`: map, tanks, bullets, eagle, HUD
- `hud.py`: lives, score, remaining enemies, current level
- `debug_overlay.py`: optional path previews, current algorithm labels, decision timers, pruning stats
- `screens.py`: menu, pause, game over, victory

UI principle:
- Debug information must be optional so the default experience stays clean and playable

### 8. `tests/`

Purpose: protect the rules that are easiest to regress and hardest to debug visually.

Test priorities:
- Collision and movement legality
- Bullet swept-path hit detection
- Pathfinding correctness on representative tile maps
- CSP generator constraints
- Boss phase depth switching and alpha-beta pruning metrics
- Win/lose conditions and enemy wave progression

## Implementation sequence

1. Build `config`, `core.state`, and `world.tiles` so the domain model is explicit.
2. Implement fixed-level loading, collision, and continuous movement with alignment assist.
3. Add player controls, bullet logic, and win/lose handling for a single playable level.
4. Add BFS, then Greedy, then A* enemies, validating that their behavior is visibly distinct.
5. Add wave management and map mutation from destructible bricks.
6. Add the boss arena and Minimax with alpha-beta pruning plus debug metrics.
7. Add CSP map generation and wire it into simulation/debug workflows or extra levels.
8. Add overlays, balancing passes, and automated tests around the most failure-prone mechanics.

## Data contracts

Use a single in-memory state model with these core records:

- `GameState`: current mode, level, tile map, eagle state, player state, enemy list, bullet list, timers, score, lives, outcome
- `TankState`: id, role, position, facing, HP, speed, cooldowns, current intent, optional current plan
- `BulletState`: owner, position, direction, speed, active flag
- `LevelSpec`: tile grid, player spawn, enemy spawns, wave definition, boss settings

This is enough to support both live rendering and AI evaluation without coupling either side to framework-specific objects.

## Risks to manage

- Continuous movement on a tile map can create corner-clipping bugs unless collision and alignment are designed together.
- Frequent replanning can damage frame stability; decision ticks must cap AI work.
- Minimax over the full live game state can become too expensive; the boss arena and reduced search state should stay intentionally small.
- Random map generation can create valid-but-bad layouts unless readability and pacing constraints are checked in addition to path existence.
