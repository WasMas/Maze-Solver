# Maze Lab

A Python desktop demonstration and reproducible classical-search benchmark for a future reinforcement-learning project. No pip packages required. Python 3.10+ with Tkinter is needed (the standard Windows Python installer includes Tkinter).

## Run

From a terminal in this folder:

```powershell
python main.py
```

If your Windows installation uses the Python launcher, substitute `py` for `python`. If neither command exists, install Python with the Tcl/Tk component and enable its PATH option, then reopen your terminal.

1. Choose grid size, then **Generate** to create a fresh random maze.
2. Select BFS, DFS, or A*, then **Solve / animate**. Choose **1×, 1.25×, 1.5×, 2×, or 4×** to change animation speed, including while it is running. Multipliers shorten the delay between animation steps; rendering time also affects actual playback speed.
3. Use **Click sets → Start/Goal** and click an open cell to change endpoints.
4. **Compare all** evaluates all three algorithms on the identical maze and endpoints; it displays the BFS solution.

Endpoint or maze changes clear old measurements. Seed controls and CSV export are omitted from the desktop interface for now; the separate benchmark command still supports reproducible experiments and CSV output.

Green is start, red is goal, blue is explored space, and gold is the solution. Exploration animation replays a completed search; timings measure the search itself, excluding animation. Search runs locally and requires no internet.

## Reproducible experiments

```powershell
python benchmark.py --size 21 --mazes 30 --repeats 5
python benchmark.py --size 31 --mazes 30 --repeats 5 --output results/baseline_31.csv
python -m unittest discover -s tests -v
```

The benchmark uses seeds 0–29, one warm-up per algorithm/maze, and averages five timed repetitions. It reports success rate, path length in moves, explored cells, and search time. Small timing differences are noisy and hardware-dependent; emphasize path quality and explored cells. The generator guarantees connectivity, so success on these mazes is expected rather than evidence of broad robustness.

Initial benchmark CSV files for sizes 11, 21, and 31 are included in `results/`. See [measured results and interpretation](results/summary.md).

## Algorithms and representation

- Grid: `1` = wall, `0` = traversable cell; coordinates are `(row, column)`.
- Movement: four cardinal directions, with uniform unit cost.
- Generation: iterative randomized depth-first carving, then extra corridor openings (default probability 0.08) to create cycles and alternative routes. Size is odd and includes boundary walls.
- BFS: shortest path for this unit-cost environment.
- DFS: valid path, with no shortest-path guarantee.
- A*: shortest path using Manhattan distance, which is admissible and consistent for these movements. Ties use distance then coordinates, so the explored count depends on tie-breaking.
- Explored cells count unique nodes removed from the frontier and processed, including the goal. Path length counts moves, not cells.

`maze_project/core.py` contains generation and search, `main.py` contains the UI, `benchmark.py` runs experiments, and `tests/test_core.py` checks correctness. The UI uses Tkinter and the project uses only Python's standard library.

## Scope and next stage

This project implements the environment and classical baselines; it does not train an ML model. Classical maze solving is a graph-search problem; the learning component will be learning a navigation policy through interaction.
