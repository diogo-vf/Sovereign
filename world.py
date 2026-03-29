"""
world.py
--------
World: manages the NxM hex grid and the simulation tick loop.
"""

from __future__ import annotations
import random
from abstracts import AbstractAgent, AbstractHexagon
from entities import Terrain, NPC


class World:
    """
    Holds the hex grid and drives the simulation.

    Grid layout: offset coordinates (even-r offset for flat-top hexagons).
    Neighbors are the 6 adjacent hexagons (boundary-aware).
    """

    def __init__(self, n: int, m: int, fertility: float = 1.0, seed: int = 42):
        self.n = n          # columns
        self.m = m          # rows
        random.seed(seed)

        # Build grid
        self.grid: dict[tuple[int, int], Terrain] = {}
        self._build_grid(fertility)
        self._link_neighbors()

        self.agents: list[AbstractAgent] = []
        self.tick_count: int = 0
        self.population_history: list[int] = []   # alive agents per tick

    # ------------------------------------------------------------------
    # Grid construction
    # ------------------------------------------------------------------

    def _build_grid(self, fertility: float) -> None:
        for x in range(self.n):
            for y in range(self.m):
                # Slight fertility variation per tile (±20%) for interest
                f = fertility * random.uniform(0.8, 1.2)
                self.grid[(x, y)] = Terrain(x, y, fertility=f)

    def _hex_neighbors_coords(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Return valid neighbor coordinates for offset hex grid (even-r).
        Directions differ for even/odd rows.
        """
        if y % 2 == 0:
            directions = [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,-1)]
        else:
            directions = [(1,0),(-1,0),(0,1),(0,-1),(1, 1),(-1, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.grid:
                neighbors.append((nx, ny))
        return neighbors

    def _link_neighbors(self) -> None:
        for (x, y), tile in self.grid.items():
            for coords in self._hex_neighbors_coords(x, y):
                tile.add_neighbor(self.grid[coords])

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    def place_agent(self, agent: AbstractAgent, x: int, y: int) -> None:
        tile = self.grid[(x, y)]
        tile.enter(agent)
        agent.position = tile
        self.agents.append(agent)

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------

    def step(self) -> None:
        """Advance the simulation by one tick."""
        # 1. All tiles regenerate resources
        for tile in self.grid.values():
            tile.tick()

        # 2. All agents act (iterate over a snapshot — list may grow)
        for agent in list(self.agents):
            if agent.is_alive():
                agent.act()
            else:
                # Pad history with NaN so all series stay aligned to tick count
                if hasattr(agent, 'history'):
                    for key in agent.history:
                        if key == "position":
                            agent.history[key].append(None)
                        else:
                            agent.history[key].append(float('nan'))

        # 3. Handle divisions
        newborns = []
        for agent in list(self.agents):
            if hasattr(agent, "ready_to_divide") and agent.ready_to_divide:
                child = agent.divide()
                if child is not None:
                    newborns.append(child)
        self.agents.extend(newborns)

        # 4. Remove dead agents from their tile
        for agent in list(self.agents):
            if not agent.is_alive() and agent.position is not None:
                agent.position.leave(agent)

        # 5. Track population
        alive = sum(1 for a in self.agents if a.is_alive())
        self.population_history.append(alive)

        self.tick_count += 1

    def run(self, ticks: int) -> None:
        """Run the simulation for `ticks` steps."""
        for _ in range(ticks):
            self.step()
            if self.population_history[-1] == 0:
                print(f"All agents died at tick {self.tick_count}.")
                break

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> None:
        print(f"\n=== World summary after {self.tick_count} ticks ===")
        for agent in self.agents:
            status = "ALIVE" if agent.is_alive() else "DEAD"
            print(f"  {agent}  [{status}]")