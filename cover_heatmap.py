"""
Cover image: 8x8 SAR probability heat map, searched sectors greyed out.
Uses the real World class from sar_harness.py, so the picture shows genuine Bayesian updates.

  python cover_heatmap.py                  # 10 greedy dispatches, saves cover_heatmap.png
  python cover_heatmap.py --dispatches 14 --seed 7 --out cover.png
"""
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import sar_harness as sar

def build_world(seed, dispatches):
    world = sar.World(seed)
    for _ in range(dispatches):
        # greedy policy: search the most likely sector right now
        cell = max(world.prob, key=world.prob.get)
        if world.apply_search(cell):      # subject found early -> stop
            break
    return world

def draw(world, out, title=True):
    n = sar.GRID
    grid = np.zeros((n, n))
    for (x, y), p in world.prob.items():
        grid[y, x] = p                    # row = y, column = x

    fig, ax = plt.subplots(figsize=(10, 12), dpi=200)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    im = ax.imshow(grid, cmap="YlOrRd", origin="upper", extent=(0, n, n, 0), vmin=0)

    # grey out searched sectors: translucent, because a miss does NOT rule a sector out
    for (x, y), times in world.searched.items():
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor="#64748b",
                               alpha=0.80, edgecolor="none", zorder=3))
        ax.plot([x + .25, x + .75], [y + .25, y + .75], color="#e2e8f0", lw=2, zorder=4)
        ax.plot([x + .25, x + .75], [y + .75, y + .25], color="#e2e8f0", lw=2, zorder=4)

    # last known position
    lx, ly = world.lkp
    ax.scatter(lx + .5, ly + .5, s=260, marker="*", color="#38bdf8",
               edgecolor="white", linewidth=1.2, zorder=5)

    # grid lines
    for i in range(n + 1):
        ax.axhline(i, color="#0f172a", lw=2.5, zorder=6)
        ax.axvline(i, color="#0f172a", lw=2.5, zorder=6)

    ax.set_xlim(0, n); ax.set_ylim(n, 0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    if title:
        fig.suptitle("Your AI agent is not the product", color="white",
                     fontsize=26, fontweight="bold", y=0.955)
        ax.set_title(f"Search-and-rescue probability map after {sum(world.searched.values())} dispatches  |  "
                     f"POS {world.pos:.0%}", color="#cbd5e1", fontsize=14, pad=14)

    # --- make the picture explain itself ---
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02, ticks=[grid.min(), grid.max()])
    cbar.ax.set_yticklabels(["lower", "higher"], color="#cbd5e1", fontsize=12)
    cbar.set_label("Chance the missing person is in this sector", color="#cbd5e1", fontsize=12)
    cbar.outline.set_visible(False)

    unsearched = sum(p for c, p in world.prob.items() if world.searched[c] == 0)
    handles = [
        Line2D([0], [0], marker="*", color="none", markerfacecolor="#38bdf8",
               markeredgecolor="white", markersize=16, label="Last known position"),
        Patch(facecolor="#64748b", edgecolor="#e2e8f0", label="Already searched (x). Missed once, not ruled out"),
        Patch(facecolor="#800026", label="Still-likely sector, not yet searched"),
    ]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=1,
                    frameon=False, fontsize=12, labelcolor="#e2e8f0")
    fig.text(0.5, 0.025,
             f"Teams have searched {len(world.searched)} of {n*n} sectors,\n"
             f"but {unsearched:.0%} of the remaining probability is still unsearched.",
             ha="center", color="#fbbf24", fontsize=14, fontweight="bold", linespacing=1.5)
    fig.tight_layout(rect=(0, 0.15, 1, 0.94))
    fig.savefig(out, facecolor=fig.get_facecolor())
    print(f"saved {out}  (POS {world.pos:.0%}, searched {len(world.searched)} sectors)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--dispatches", type=int, default=10)
    ap.add_argument("--out", default="cover_heatmap.png")
    ap.add_argument("--no-title", action="store_true")
    a = ap.parse_args()
    draw(build_world(a.seed, a.dispatches), a.out, title=not a.no_title)
