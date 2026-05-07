# Architecture Diagram

## Module relationship

```text
                +------------------+
                |      main.py     |
                | pygame bootstrap |
                +---------+--------+
                          |
                          v
                +------------------+
                |   game/modes/    |
                | play, sim, flow  |
                +---------+--------+
                          |
                          v
                +------------------+
                |   game/core/     |
                | state + loop     |
                +----+--------+----+
                     |        |
          reads/writes|        |emits state to
                     v        v
           +------------+   +-------------+
           | game/world/|   |  game/ui/   |
           | map rules  |   | render/HUD  |
           +-----+------+   +-------------+
                 |
      validates  |
      movement   |
                 v
           +------------+
           | entities/  |
           | tanks/bull |
           +-----+------+
                 |
         requests|
         actions |
                 v
            +---------+
            |   ai/   |
            | planners|
            +---------+
```

## Tick flow

```text
Input
  ->
Timers/Cooldowns
  ->
Enemy AI Decision Tick
  ->
Validate Intents
  ->
Tank Movement
  ->
Bullet Spawn
  ->
Bullet Movement
  ->
Collision / Damage / Brick Break
  ->
Enemy Spawn / Wave Progress
  ->
Win/Lose Check
  ->
Render
```

## Dependency rules

- `ui/` may read state but should not own game rules.
- `ai/` may inspect state snapshots but should not mutate state directly.
- `entities/` produce intents; `core/` and `world/` decide whether those intents are legal.
- `world/` should stay framework-agnostic so collision and map logic are testable.
