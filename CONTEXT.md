# Battle City AI

A human-playable Battle City-inspired tank combat game where one human-controlled tank defends the eagle against AI-controlled enemy tanks. The project exists to make AI behavior visible inside live gameplay rather than as a simulation-only exercise.

## Language

**Battle City-Inspired AI Game**:
A playable tank combat game that borrows Battle City's core loop without requiring clone-level fidelity.
_Avoid_: Strict clone, prototype-only demo, algorithm sandbox

**Playable Match**:
The primary real-time game mode where the human-controlled tank fights AI-controlled enemies on a single level.
_Avoid_: Benchmark run, autoplay match, simulation

**Simulation Mode**:
An optional non-primary mode that reuses the same rules to inspect or compare AI behavior.
_Avoid_: Main game, normal play

**Tile Map**:
A fixed grid of terrain and structures that defines navigation, cover, and collision boundaries.
_Avoid_: Freeform arena, unbounded canvas

**Eagle**:
The base objective that the player must defend and the enemy force tries to destroy.
_Avoid_: Goal marker, endpoint, capture flag

**Player Tank**:
The single tank controlled by the human during a **Playable Match**.
_Avoid_: Agent, bot, autonomous player

**Enemy Tank**:
Any non-player tank controlled by an AI behavior during a **Playable Match**.
_Avoid_: NPC vehicle, bot opponent

**Basic Tank**:
An **Enemy Tank** that follows a shortest-path attack pattern using BFS.
_Avoid_: Generic enemy, default bot

**Fast Tank**:
An **Enemy Tank** that rushes its target using Greedy Best-First Search.
_Avoid_: Speed-only variant, random chaser

**Armor Tank**:
An **Enemy Tank** that uses A* and survives multiple hits before being destroyed.
_Avoid_: Heavy bot, boss-lite

**Boss Tank**:
A single high-health **Enemy Tank** that uses Minimax with alpha-beta pruning in the boss level.
_Avoid_: Final wave, scripted enemy

**Continuous Movement**:
Tank and projectile motion that updates in pixel space while staying constrained by the **Tile Map**.
_Avoid_: Tile snapping, turn-by-turn stepping

**Solid Collision**:
A movement rule where tanks never overlap walls, the **Eagle**, or other tanks.
_Avoid_: Ghosting, pass-through collision, soft overlap

**Alignment Assist**:
A small automatic nudge that helps a tank complete a valid turn into an open lane without weakening **Solid Collision**.
_Avoid_: Auto-pathing, forced correction

**Projectile**:
A visible bullet that travels in a straight cardinal direction and resolves hits against the swept path it crosses.
_Avoid_: Instant hit, hidden damage event, tile jump

**Decision Tick**:
The discrete moment when an **Enemy Tank** may re-evaluate its plan or choose a new action.
_Avoid_: Render frame, per-pixel recalculation

**Line-of-Sight Shot**:
A firing opportunity where a tank has a clear straight path to its target along a row or column.
_Avoid_: Area attack, predictive shot

**Enemy Wave**:
The controlled sequence in which **Enemy Tanks** enter a **Playable Match** from spawn positions.
_Avoid_: Infinite swarm, random flood

**CSP Map Generator**:
A level-building process that creates valid **Tile Maps** while preserving playability constraints.
_Avoid_: Random wall scatter, cosmetic generator

**Gameplay Quality**:
The combination of responsive movement, reliable collisions, readable levels, and clear AI behavior during live play.
_Avoid_: Algorithm-only output, debug-first experience

## Relationships

- The **Battle City-Inspired AI Game** is delivered primarily through a **Playable Match**
- A **Playable Match** contains exactly one **Player Tank**
- A **Playable Match** contains one or more **Enemy Tanks**
- A **Playable Match** is played on exactly one **Tile Map**
- The **Eagle** exists on the **Tile Map** as the defended base objective
- **Enemy Tanks** attack the **Eagle** and may also engage the **Player Tank**
- A **Playable Match** contains one or more **Projectiles**
- **Continuous Movement** happens within the constraints of the **Tile Map**
- **Solid Collision** applies to the **Player Tank**, **Enemy Tanks**, and the **Eagle**
- **Alignment Assist** supports **Continuous Movement** without weakening **Solid Collision**
- A **Projectile** moves continuously but resolves contact along the swept path it crosses
- **Enemy Tanks** replan on a **Decision Tick**, not on every render frame
- A **Basic Tank** uses BFS, a **Fast Tank** uses Greedy Best-First Search, and an **Armor Tank** uses A*
- A **Boss Tank** uses Minimax with alpha-beta pruning and appears only in the boss level
- The **CSP Map Generator** must produce a **Tile Map** where a path from spawn to the **Eagle** exists
- **Simulation Mode** reuses the same rules as a **Playable Match** but is not the primary experience
- **Gameplay Quality** is prioritized alongside visible AI differentiation

## Example dialogue

> **Dev:** "Should the enemies feel like separate algorithms even if the player only sees one tank sprite?"
> **Domain expert:** "Yes. A **Basic Tank**, **Fast Tank**, and **Armor Tank** must behave differently enough in a **Playable Match** that the player can see the difference without opening a debug view."

## Flagged ambiguities

- "AI project" could mean fully autonomous play on both sides; resolved: the primary product is a **Playable Match** with one human-controlled **Player Tank**
- "Battle City" could imply clone-level fidelity; resolved: the target is a **Battle City-Inspired AI Game**, not a strict remake
- "smooth movement" could imply gridless physics; resolved: tanks and bullets use **Continuous Movement** while remaining constrained by the **Tile Map**
- "responsive movement" could imply permissive turning or overlap; resolved: the game uses **Solid Collision** with limited **Alignment Assist**
- "simple shooting" could imply non-physical hits; resolved: the game uses visible **Projectiles** with swept-path hit checks
- "map generation" could imply any random layout; resolved: the **CSP Map Generator** must preserve playability constraints, especially a valid path to the **Eagle**
