"""
main.py
-------
Entry point: configure parameters, run simulation, plot results.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from world import World
from entities import NPC


# -----------------------------------------------------------------------
# Parameters
# -----------------------------------------------------------------------

WORLD_N      = 50       # grid columns
WORLD_M      = 50     # grid rows
FERTILITY    = 0.5      # base fertility (resource regen per tick)
SEED         = 42
TICKS        = 1000

NPC_PARAMS = dict(
    energy           = 50.0,
    metabolism       = 8.0,    # métabolisme élevé → pression constante
    energy_threshold = 49,
    energy_cap       = 150.0,  # cap bas → divisions fréquentes → compétition rapide
    appetite_cereals = 2.5,
    appetite_water   = 4.5,
    energy_per_cereal= 2.3,
    energy_per_water = 0.8,
    synergy          = 1.2,
    alpha            = 2.5,    # travail coûteux → difficile de rentabiliser
    gamma            = 1.5,    # déplacement coûteux → mouvement pénalisant
)


# -----------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------

def main():
    world = World(WORLD_N, WORLD_M, fertility=FERTILITY, seed=SEED)

    npc = NPC(**NPC_PARAMS)
    world.place_agent(npc, x=0, y=0)

    print(f"Starting simulation: {WORLD_N}x{WORLD_M} grid, {TICKS} ticks")
    world.run(TICKS)
    world.summary()

    plot_results(npc, world)


# -----------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------

def plot_results(npc: NPC, world: World):
    ticks     = range(len(npc.history["energy"]))
    pop_ticks = range(len(world.population_history))

    fig = plt.figure(figsize=(14, 12))
    fig.suptitle(f"NPC Simulation — {TICKS} ticks", fontsize=14, fontweight="bold")
    gs  = gridspec.GridSpec(4, 2, figure=fig, hspace=0.5, wspace=0.35)

    # --- 1. Population over time (full width) ---
    ax0 = fig.add_subplot(gs[0, :])
    ax0.plot(pop_ticks, world.population_history, color="#E91E63", linewidth=2)
    ax0.fill_between(pop_ticks, world.population_history, alpha=0.15, color="#E91E63")
    ax0.set_title("Population (alive agents)")
    ax0.set_xlabel("Tick")
    ax0.set_ylabel("Count")
    ax0.set_ylim(bottom=0)
    ax0.grid(alpha=0.3)

    # --- 2. Energy of first NPC ---
    ax1 = fig.add_subplot(gs[1, :])
    ax1.plot(ticks, npc.history["energy"], color="#2196F3", linewidth=2)
    ax1.axhline(npc.energy_threshold, color="red",    linestyle="--", linewidth=1, label="death threshold")
    ax1.axhline(npc.energy_cap,       color="orange", linestyle="--", linewidth=1, label="division cap")
    ax1.set_title("Energy level (NPC #1)")
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Energy")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # --- 3. Work effort ---
    ax2 = fig.add_subplot(gs[2, 0])
    ax2.plot(ticks, npc.history["work_cereals"], label="cereals", color="#FF9800")
    ax2.plot(ticks, npc.history["work_water"],   label="water",   color="#03A9F4")
    ax2.set_title("Work effort (NPC #1)")
    ax2.set_xlabel("Tick")
    ax2.set_ylabel("Work units")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # --- 4. Consumption ---
    ax3 = fig.add_subplot(gs[2, 1])
    ax3.plot(ticks, npc.history["consumed_cereals"], label="cereals", color="#FF9800")
    ax3.plot(ticks, npc.history["consumed_water"],   label="water",   color="#03A9F4")
    ax3.set_title("Consumption (NPC #1)")
    ax3.set_xlabel("Tick")
    ax3.set_ylabel("Units consumed")
    ax3.legend()
    ax3.grid(alpha=0.3)

    # --- 5. Utility ---
    ax4 = fig.add_subplot(gs[3, 0])
    ax4.plot(ticks, npc.history["utility"], color="#9C27B0", linewidth=1.5)
    ax4.set_title("Realised utility (NPC #1)")
    ax4.set_xlabel("Tick")
    ax4.set_ylabel("U")
    ax4.set_ylim(bottom=0)
    ax4.grid(alpha=0.3)

    # --- 6. Movement ---
    ax5 = fig.add_subplot(gs[3, 1])
    moves = np.array(npc.history["moved"])
    ax5.bar(ticks, moves, color="#4CAF50", alpha=0.7, width=0.8)
    ax5.set_title(f"Movement events (NPC #1, total: {moves.sum()})")
    ax5.set_xlabel("Tick")
    ax5.set_ylabel("Moved (1=yes)")
    ax5.set_yticks([0, 1])
    ax5.grid(alpha=0.3, axis="y")

    folder = "outputs"
    if not os.path.exists(folder):
        os.makedirs(folder)
    plt.savefig(f"{folder}/simulation_results.png", dpi=150, bbox_inches="tight")
    print("\nPlot saved → simulation_results.png")
    plt.show()


if __name__ == "__main__":
    main()