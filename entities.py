"""
entities.py
-----------
Concrete implementations: Terrain hexagon and NPC agent.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from abstracts import AbstractHexagon, AbstractAgent

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Terrain
# ---------------------------------------------------------------------------

@dataclass
class ResourceSlot:
    """A single resource available on a Terrain hex."""
    name: str
    quantity: float         # current stock on the tile
    fertility: float        # units regenerated per tick
    capacity: float         # max stock the tile can hold


class Terrain(AbstractHexagon):
    """
    A terrain hexagon with climate, type, fertility, and harvestable resources.

    For this first simulation:
      - move_cost = 1 (fixed)
      - Two resources: cereals and water
      - Fertility = regeneration rate per tick (same for both resources)
      - Resources regenerate each tick up to their capacity
    """

    TRAVERSE_COST: float = 1.0

    def __init__(
        self,
        x: int,
        y: int,
        climate: str = "temperate",
        terrain_type: str = "plain",
        fertility: float = 1.0,
        density: int = 4,
    ):
        super().__init__(x, y, density)
        self.climate = climate
        self.terrain_type = terrain_type
        self.fertility = fertility

        # Two resources with the same fertility for now
        cereal_capacity = fertility * 20
        water_capacity  = fertility * 20

        self.resources: dict[str, ResourceSlot] = {
            "cereals": ResourceSlot("cereals", cereal_capacity, fertility, cereal_capacity),
            "water":   ResourceSlot("water",   water_capacity,  fertility, water_capacity),
        }

    def move_cost(self) -> float:
        return self.TRAVERSE_COST

    def tick(self) -> None:
        """Regenerate resources up to their capacity."""
        for slot in self.resources.values():
            slot.quantity = min(slot.quantity + slot.fertility, slot.capacity)

    def extract(self, resource: str, amount: float) -> float:
        """
        Remove `amount` units of `resource` from the tile.
        Returns the actual amount extracted (capped by availability).
        """
        slot = self.resources[resource]
        extracted = min(amount, slot.quantity)
        slot.quantity -= extracted
        return extracted

    def __repr__(self) -> str:
        res = {k: f"{v.quantity:.1f}" for k, v in self.resources.items()}
        return f"Terrain({self.x},{self.y}) | {res}"


# ---------------------------------------------------------------------------
# NPC
# ---------------------------------------------------------------------------

class NPC(AbstractAgent):
    """
    A single non-player character agent.

    Utility function (maximized each tick):
        U = X*c_c + Y*c_w + S*c_c*c_w  -  alpha*(w_c + w_w)  -  gamma*move_cost
    where:
        c_i   = cereals / water consumed this tick
        w_i   = work effort allocated to resource i
        alpha = energy cost per unit of work effort
        gamma = energy cost multiplier for movement

    The NPC solves this myopically (greedy, no lookahead) each tick.
    """

    def __init__(
        self,
        energy: float           = 50.0,
        metabolism: float       = 2.0,
        energy_threshold: float = 5.0,
        energy_cap: float       = 200.0,  # division threshold
        appetite_cereals: float = 5.0,
        appetite_water: float   = 5.0,
        # Energy conversion coefficients
        energy_per_cereal: float = 3.0,   # X
        energy_per_water: float  = 2.0,   # Y
        synergy: float           = 1.5,   # S (bilinear bonus)
        # Cost coefficients
        alpha: float = 1.0,               # energy cost per unit of work
        gamma: float = 1.0,               # multiplier on move cost
    ):
        super().__init__(energy, metabolism, energy_threshold)

        self.energy_cap        = energy_cap
        self.appetite_cereals  = appetite_cereals
        self.appetite_water    = appetite_water
        self.energy_per_cereal = energy_per_cereal
        self.energy_per_water  = energy_per_water
        self.synergy           = synergy
        self.alpha             = alpha
        self.gamma             = gamma

        self.ready_to_divide: bool = False   # flag checked by World each tick

        # Personal inventory
        self.inventory: dict[str, float] = {"cereals": 0.0, "water": 0.0}

        # History for plotting
        self.history: dict[str, list] = {
            "energy":         [],
            "work_cereals":   [],
            "work_water":     [],
            "consumed_cereals": [],
            "consumed_water": [],
            "utility":        [],
            "moved":          [],
            "position":       [],
        }

    # ------------------------------------------------------------------
    # Core utility calculation (pure function — no side effects)
    # ------------------------------------------------------------------

    def _utility(
        self,
        c_c: float,
        c_w: float,
        w_c: float,
        w_w: float,
        move_cost: float,
    ) -> float:
        gain = (
            self.energy_per_cereal * c_c
            + self.energy_per_water  * c_w
            + self.synergy           * c_c * c_w
        )
        cost = self.alpha * (w_c + w_w) + self.gamma * move_cost
        return gain - cost

    # ------------------------------------------------------------------
    # Greedy optimisation (closed-form for linear + min constraints)
    # ------------------------------------------------------------------

    def _optimal_work(self, tile: "Terrain") -> tuple[float, float]:
        """
        Compute optimal work effort for each resource on `tile`.

        Because utility is linear in consumption (before the min clip),
        the NPC always wants to fill its appetite.  The optimal work effort
        is therefore the minimum effort needed to reach appetite given its
        current inventory, capped by what the tile can supply.

        w_i* = max(0,  appetite_i - inventory_i) / fertility_i
        but we also cannot extract more than the tile holds.
        """
        results = {}
        for res, appetite in [("cereals", self.appetite_cereals),
                               ("water",   self.appetite_water)]:
            slot = tile.resources[res]
            needed   = max(0.0, appetite - self.inventory[res])
            # How much work to produce `needed` units? produced = w * fertility
            if slot.fertility > 0:
                w = needed / slot.fertility
            else:
                w = 0.0
            # Cap: cannot extract more than what is on the tile
            max_extract = slot.quantity
            w = min(w, max_extract / slot.fertility if slot.fertility > 0 else 0.0)
            results[res] = w
        return results["cereals"], results["water"]

    # ------------------------------------------------------------------
    # AbstractAgent interface
    # ------------------------------------------------------------------

    def produce(self, hexagon: AbstractHexagon) -> dict[str, float]:
        """Extract resources from the current tile based on work effort."""
        if not isinstance(hexagon, Terrain):
            return {"cereals": 0.0, "water": 0.0}

        w_c, w_w = self._optimal_work(hexagon)
        extracted = {
            "cereals": hexagon.extract("cereals", w_c * hexagon.resources["cereals"].fertility),
            "water":   hexagon.extract("water",   w_w * hexagon.resources["water"].fertility),
        }
        for res, qty in extracted.items():
            self.inventory[res] += qty
        return extracted, w_c, w_w

    def consume(self) -> float:
        """Consume from inventory up to appetite; return energy gained."""
        c_c = min(self.inventory["cereals"], self.appetite_cereals)
        c_w = min(self.inventory["water"],   self.appetite_water)
        self.inventory["cereals"] -= c_c
        self.inventory["water"]   -= c_w
        gain = (
            self.energy_per_cereal * c_c
            + self.energy_per_water  * c_w
            + self.synergy           * c_c * c_w
        )
        return gain, c_c, c_w

    def _choose_move(self) -> tuple[bool, "AbstractHexagon | None"]:
        """
        Evaluate whether to move to a neighboring tile.
        The NPC moves if a neighbor offers a better expected utility than staying.
        'Better' = higher total available resources / move_cost ratio.
        """
        if not isinstance(self.position, Terrain):
            return False, None

        def tile_score(tile: Terrain) -> float:
            return (
                tile.resources["cereals"].quantity + tile.resources["water"].quantity
            )

        current_score = tile_score(self.position)
        best_score    = current_score
        best_tile     = None

        for neighbor in self.position.neighbors:
            if isinstance(neighbor, Terrain) and not neighbor.is_full():
                # Net score: resource richness minus movement cost
                net = tile_score(neighbor) - self.gamma * neighbor.move_cost()
                if net > best_score:
                    best_score = net
                    best_tile  = neighbor

        if best_tile is not None:
            return True, best_tile
        return False, None

    def act(self) -> None:
        """
        Main tick action:
        1. Decide whether to move
        2. Produce on current tile
        3. Consume from inventory
        4. Apply metabolism
        5. Record history
        """
        if not self.is_alive() or self.position is None:
            return

        # --- Movement decision ---
        moved      = False
        move_cost  = 0.0
        will_move, target = self._choose_move()
        if will_move and target is not None:
            self.position.leave(self)
            target.enter(self)
            self.position = target
            move_cost = self.gamma * target.move_cost()
            self.energy -= move_cost
            moved = True

        # --- Production ---
        extracted, w_c, w_w = self.produce(self.position)

        # --- Consumption ---
        gain, c_c, c_w = self.consume()
        self.energy += gain

        # --- Metabolism ---
        self.apply_metabolism()

        # --- Utility realised this tick ---
        u = self._utility(c_c, c_w, w_c, w_w, move_cost)

        # --- Energy cap: flag for division ---
        if self.energy >= self.energy_cap:
            self.energy = self.energy_cap / 2
            self.ready_to_divide = True

        # --- Record (always, including death tick) ---
        self.history["energy"].append(self.energy)
        self.history["work_cereals"].append(w_c)
        self.history["work_water"].append(w_w)
        self.history["consumed_cereals"].append(c_c)
        self.history["consumed_water"].append(c_w)
        self.history["utility"].append(u)
        self.history["moved"].append(int(moved))
        self.history["position"].append(self.position.coords)

        # --- Stop acting after death ---
        if not self.is_alive():
            return

    def divide(self) -> "NPC | None":
        """
        Spawn a clone on a free neighboring tile.
        Both parent and child start at energy_cap / 2 (parent already set in act()).
        Returns the new NPC if division succeeded, None if no free neighbor.
        """
        free_neighbors = [
            n for n in self.position.neighbors
            if isinstance(n, Terrain) and not n.is_full()
        ]
        if not free_neighbors:
            return None  # no room — division blocked

        target = free_neighbors[0]
        child = NPC(
            energy           = self.energy,   # already halved
            metabolism       = self.metabolism,
            energy_threshold = self.energy_threshold,
            energy_cap       = self.energy_cap,
            appetite_cereals = self.appetite_cereals,
            appetite_water   = self.appetite_water,
            energy_per_cereal= self.energy_per_cereal,
            energy_per_water = self.energy_per_water,
            synergy          = self.synergy,
            alpha            = self.alpha,
            gamma            = self.gamma,
        )
        target.enter(child)
        child.position = target
        self.ready_to_divide = False
        return child

    def __repr__(self) -> str:
        inv = {k: f"{v:.1f}" for k, v in self.inventory.items()}
        return f"NPC(energy={self.energy:.2f}, inv={inv})"