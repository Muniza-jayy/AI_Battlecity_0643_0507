# Folder Structure

## Recommended layout

```text
Finalproject/
├── README.md
├── CONTEXT.md
├── ARCHITECTURE_PLAN.md
├── project.prd
├── requirements.txt
├── main.py
├── docs/
│   ├── FOLDER_STRUCTURE.md
│   ├── ARCHITECTURE_DIAGRAM.md
│   ├── MILESTONE_CHECKLIST.md
│   ├── DEPENDENCIES.md
│   └── FIRST_IMPLEMENTATION_TASKS.md
├── assets/
│   ├── sprites/
│   ├── fonts/
│   ├── sounds/
│   └── maps/
├── config/
│   ├── settings.py
│   ├── balance.py
│   └── levels.py
├── game/
│   ├── core/
│   │   ├── state.py
│   │   ├── loop.py
│   │   ├── events.py
│   │   └── timers.py
│   ├── world/
│   │   ├── tiles.py
│   │   ├── map_loader.py
│   │   ├── map_generator.py
│   │   ├── collision.py
│   │   └── alignment.py
│   ├── entities/
│   │   ├── tank.py
│   │   ├── player.py
│   │   ├── enemy.py
│   │   └── bullet.py
│   ├── ai/
│   │   ├── graph.py
│   │   ├── heuristics.py
│   │   ├── bfs_agent.py
│   │   ├── greedy_agent.py
│   │   ├── astar_agent.py
│   │   ├── minimax_agent.py
│   │   ├── line_of_sight.py
│   │   └── evaluation.py
│   ├── modes/
│   │   ├── play_mode.py
│   │   ├── simulation_mode.py
│   │   └── level_flow.py
│   └── ui/
│       ├── renderer.py
│       ├── hud.py
│       ├── debug_overlay.py
│       └── screens.py
└── tests/
    ├── test_collision.py
    ├── test_projectiles.py
    ├── test_pathfinding.py
    ├── test_generator.py
    └── test_game_rules.py
```

## Why this split

- `config/` holds constants and avoids magic numbers.
- `game/core/` owns the game state and update order.
- `game/world/` owns map logic, terrain, and collision rules.
- `game/entities/` owns tanks and bullets without embedding AI strategy.
- `game/ai/` isolates search algorithms and evaluation logic.
- `game/modes/` separates normal play from simulation/debug flows.
- `game/ui/` contains rendering and interface code only.
- `tests/` protects rules that should be verifiable without running the full game window.
