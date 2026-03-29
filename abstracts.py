"""
abstracts.py
------------
Abstract base classes for the simulation.
All concrete entities must inherit from these.
"""

from abc import ABC, abstractmethod
from typing import Optional


# ---------------------------------------------------------------------------
# Abstract Hexagon
# ---------------------------------------------------------------------------

class AbstractHexagon(ABC):
    """
    A hexagonal cell in the world grid.

    Coordinates use axial hex coordinates (q, r) mapped from (x, y).
    Each hexagon has a type, a maximum agent density, and a list of neighbors.
    """

    def __init__(self, x: int, y: int, density: int = 1):
        self.x = x
        self.y = y
        self.density = density          # max simultaneous agents
        self.neighbors: list["AbstractHexagon"] = []
        self._agents: list["AbstractAgent"] = []

    @property
    def coords(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def hex_type(self) -> str:
        """Return the type label of this hexagon (e.g. 'terrain', 'void')."""
        return self.__class__.__name__.lower()

    def add_neighbor(self, hexagon: "AbstractHexagon") -> None:
        if hexagon not in self.neighbors:
            self.neighbors.append(hexagon)

    def is_full(self) -> bool:
        return len(self._agents) >= self.density

    def enter(self, agent: "AbstractAgent") -> bool:
        """Try to place an agent on this hexagon. Returns True if successful."""
        if self.is_full():
            return False
        self._agents.append(agent)
        return True

    def leave(self, agent: "AbstractAgent") -> None:
        if agent in self._agents:
            self._agents.remove(agent)

    @abstractmethod
    def move_cost(self) -> float:
        """Energy cost for an agent to move onto this hexagon."""
        ...

    @abstractmethod
    def tick(self) -> None:
        """Update internal state of the hexagon at each simulation tick."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x}, {self.y})"


# ---------------------------------------------------------------------------
# Abstract Agent
# ---------------------------------------------------------------------------

class AbstractAgent(ABC):
    """
    A generic agent in the simulation.

    An agent has an energy level, a base metabolism, and abstract
    produce/consume methods that define its behavior each tick.
    """

    def __init__(
        self,
        energy: float,
        metabolism: float,
        energy_threshold: float = 0.0,
    ):
        self.energy = energy
        self.metabolism = metabolism
        self.energy_threshold = energy_threshold    # below this → dead
        self.position: Optional[AbstractHexagon] = None

    def is_alive(self) -> bool:
        return self.energy > self.energy_threshold

    def apply_metabolism(self) -> None:
        """Subtract base metabolic cost at each tick."""
        self.energy -= self.metabolism

    @abstractmethod
    def produce(self, hexagon: AbstractHexagon) -> dict[str, float]:
        """
        Extract resources from a hexagon.
        Returns a dict {resource_name: quantity_extracted}.
        """
        ...

    @abstractmethod
    def consume(self) -> float:
        """
        Consume resources from inventory.
        Returns the energy gained from consumption.
        """
        ...

    @abstractmethod
    def act(self) -> None:
        """
        Main decision function called each tick.
        The agent optimizes its utility by choosing work effort,
        consumption, and whether/where to move.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(energy={self.energy:.2f})"