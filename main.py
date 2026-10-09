"""Launch the desktop demo: python main.py."""
import tkinter as tk
from tkinter import ttk, messagebox
from maze_project.core import generate_maze, solve


class MazeApp:
    def __init__(self, root):
        self.root = root
        root.title("Maze Lab | Classical search baselines")
        root.geometry("1100x820")
        root.minsize(900, 700)
        self.timer = None
        self.results = []
        self.mode = tk.StringVar(value="Explore")
        self.size = tk.StringVar(value="21")
        self.algorithm = tk.StringVar(value="BFS")
        self.speed = tk.DoubleVar(value=1.0)
        self.status = tk.StringVar(value="Generate a maze, then solve or compare all three algorithms.")
        ttk.Label(root, text="MAZE LAB", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=24, pady=(18, 0))
        ttk.Label(root, text="Maze environments & classical baselines").pack(anchor="w", padx=24, pady=(0, 14))
        controls = ttk.Frame(root)
        controls.pack(fill="x", padx=24)
        for label, variable, values in [("Grid", self.size, ("11", "21", "31", "41")), ("Algorithm", self.algorithm, ("BFS", "DFS", "A*")), ("Click sets", self.mode, ("Explore", "Start", "Goal"))]:
            ttk.Label(controls, text=label).pack(side="left", padx=(0, 5))
            ttk.Combobox(controls, textvariable=variable, values=values, state="readonly", width=9).pack(side="left", padx=(0, 12))
        ttk.Button(controls, text="Generate", command=self.generate).pack(side="left", padx=5)
        actions = ttk.Frame(root)
        actions.pack(fill="x", padx=24, pady=12)
        for label, action in [("Solve / animate", self.animate), ("Compare all", self.compare), ("Clear overlay", self.clear)]:
            ttk.Button(actions, text=label, command=action).pack(side="left", padx=(0, 8))
        ttk.Label(actions, text="Speed").pack(side="left", padx=8)
        for multiplier in (1.0, 1.25, 1.5, 2.0, 4.0):
            ttk.Radiobutton(actions, text=f"{multiplier:g}×", variable=self.speed,
                            value=multiplier).pack(side="left", padx=4)
        self.canvas = tk.Canvas(root, background="#101827", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=24)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<Button-1>", self.click)
        ttk.Label(root, text="Green: start   ·   Red: goal   ·   Blue: explored   ·   Gold: solution", padding=8).pack()
        self.table = ttk.Treeview(root, columns=("algorithm", "solved", "length", "explored", "time"), show="headings", height=3)
        for key, title in zip(self.table["columns"], ("Algorithm", "Solved", "Path (moves)", "Explored cells", "Search time (ms)")):
            self.table.heading(key, text=title)
            self.table.column(key, width=150, anchor="center")
        self.table.pack(fill="x", padx=24)
        ttk.Label(root, textvariable=self.status, padding=12).pack(anchor="w")
        self.maze = None
        self.overlay = {}
        self.generate()

    def cancel(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def clear(self):
        self.cancel()
        self.overlay = {}
        self.draw()

    def reset_results(self):
        self.results = []
        self.table.delete(*self.table.get_children())

    def generate(self):
        try:
            maze = generate_maze(int(self.size.get()), seed=None)
        except ValueError as error:
            messagebox.showerror("Invalid settings", str(error))
            return
        self.clear()
        self.maze = maze
        self.reset_results()
        self.draw()
        self.status.set(f"New {maze.size} × {maze.size} maze. Click an open cell to change start or goal.")

    def draw(self):
        self.canvas.delete("all")
        if self.maze is None:
            return
        self.cell = min(self.canvas.winfo_width(), self.canvas.winfo_height()) / self.maze.size
        self.xoffset = (self.canvas.winfo_width() - self.cell * self.maze.size) / 2
        for r, row in enumerate(self.maze.grid):
            for c, wall in enumerate(row):
                color = "#19263b" if wall else self.overlay.get((r, c), "#e7edf5")
                if (r, c) == self.maze.start:
                    color = "#30bd89"
                elif (r, c) == self.maze.goal:
                    color = "#ef6571"
                x, y = self.xoffset + c * self.cell, r * self.cell
                self.canvas.create_rectangle(x, y, x + self.cell, y + self.cell, fill=color, outline="#101827", width=0.5)

    def click(self, event):
        if self.mode.get() == "Explore":
            return
        r, c = int(event.y // self.cell), int((event.x - self.xoffset) // self.cell)
        if 0 <= r < self.maze.size and 0 <= c < self.maze.size and not self.maze.grid[r][c]:
            self.clear()
            if self.mode.get() == "Start":
                self.maze.start = (r, c)
            else:
                self.maze.goal = (r, c)
            self.reset_results()
            self.draw()

    def show_results(self, results):
        self.results = results
        self.table.delete(*self.table.get_children())
        for result in results:
            self.table.insert("", "end", values=(result.algorithm, result.solved, result.path_length if result.solved else "—", len(result.explored), f"{result.elapsed_ms:.3f}"))

    def animate(self):
        self.clear()
        result = solve(self.maze, self.algorithm.get())
        self.show_results([result])
        events = [(p, "#65a5dc") for p in result.explored] + [(p, "#f8c75b") for p in result.path]
        self.status.set(f"Animating {result.algorithm}; measured search time excludes rendering.")
        def step(index=0):
            self.timer = None
            if index == len(events):
                self.status.set(f"{result.algorithm}: {result.path_length} moves, {len(result.explored)} cells explored." if result.solved else "No path found.")
                return
            position, color = events[index]
            self.overlay[position] = color
            self.draw()
            self.timer = self.root.after(max(1, round(15 / self.speed.get())), lambda: step(index + 1))
        step()

    def compare(self):
        self.clear()
        self.show_results([solve(self.maze, algorithm) for algorithm in ("BFS", "DFS", "A*")])
        self.overlay = {p: "#f8c75b" for p in self.results[0].path}
        self.draw()
        self.status.set("Same maze and endpoints for every algorithm. Showing BFS's shortest path. Timings are single-run measurements.")

if __name__ == "__main__":
    root = tk.Tk()
    MazeApp(root)
    root.mainloop()
