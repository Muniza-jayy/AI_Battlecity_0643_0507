# Dependency List

## Core runtime

- `pygame`
Purpose: game window, input, timing, rendering, sound

## Useful standard-library modules

- `dataclasses`
Purpose: lightweight state models

- `enum`
Purpose: tile types, directions, game states

- `typing`
Purpose: clear interfaces and maintainable module boundaries

- `math`
Purpose: movement, distance, and collision helpers

- `heapq`
Purpose: priority queues for Greedy Best-First Search and A*

- `collections`
Purpose: queue/deque support for BFS and timers

- `random`
Purpose: map generation and controlled spawn variation

- `json`
Purpose: loading maps or level specs from data files

- `time`
Purpose: profiling or debug metrics if needed

## Testing

- `pytest`
Purpose: unit tests for collision, pathfinding, map generation, and game rules

## Optional later dependencies

- `numpy`
Purpose: only if you later need analytics helpers or faster grid utilities
Recommendation: do not start with it

## Recommended `requirements.txt`

```text
pygame>=2.5,<3.0
pytest>=8.0,<9.0
```

## Dependency guidance

- Start with as few third-party packages as possible.
- Do not add pathfinding libraries; implement BFS, Greedy, A*, and Minimax yourself because they are part of the course objective.
- Keep game logic independent from Pygame objects so tests can run without opening a game window.
