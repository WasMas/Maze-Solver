from collections import deque
from dataclasses import dataclass
import heapq
import random
from time import perf_counter

Position = tuple[int, int]


@dataclass
class Maze:
    grid: list[list[int]]
    start: Position
    goal: Position

    @property
    def size(self):
        return len(self.grid)

    def neighbors(self, position):
        r, c = position
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == 0:
                yield nr, nc


def generate_maze(size=21, seed=42, loops=0.08):
    """Carve a connected odd-sized grid; extra openings create alternative paths."""
    if size < 5 or size % 2 == 0:
        raise ValueError("Size must be an odd integer of at least 5.")
    if not 0 <= loops <= 1:
        raise ValueError("Loop probability must be between 0 and 1.")
    rng = random.Random(seed)
    grid = [[1] * size for _ in range(size)]
    grid[1][1] = 0
    stack = [(1, 1)]
    while stack:
        r, c = stack[-1]
        candidates = [(r + dr, c + dc) for dr, dc in ((-2, 0), (0, 2), (2, 0), (0, -2))
                      if 0 < r + dr < size - 1 and 0 < c + dc < size - 1
                      and grid[r + dr][c + dc] == 1]
        if not candidates:
            stack.pop()
            continue
        nr, nc = rng.choice(candidates)
        grid[(r + nr) // 2][(c + nc) // 2] = 0
        grid[nr][nc] = 0
        stack.append((nr, nc))
    for r in range(1, size - 1):
        for c in range(1, size - 1):
            if grid[r][c] and (r % 2 != c % 2) and rng.random() < loops:
                grid[r][c] = 0
    return Maze(grid, (1, 1), (size - 2, size - 2))


@dataclass
class SearchResult:
    algorithm: str
    path: list[Position]
    explored: list[Position]
    elapsed_ms: float

    @property
    def solved(self):
        return bool(self.path)

    @property
    def path_length(self):
        return len(self.path) - 1 if self.path else None


def solve(maze, algorithm="BFS"):
    if algorithm not in ("BFS", "DFS", "A*"):
        raise ValueError("Algorithm must be BFS, DFS, or A*.")
    for r, c in (maze.start, maze.goal):
        if not (0 <= r < maze.size and 0 <= c < maze.size) or maze.grid[r][c]:
            raise ValueError("Start and goal must be open cells.")
    started = perf_counter()
    parent = {maze.start: None}
    explored = []
    distances = {maze.start: 0}
    frontier = deque([maze.start])
    heap = [(0, 0, maze.start)]
    closed = set()
    while heap if algorithm == "A*" else frontier:
        if algorithm == "A*":
            _, distance, current = heapq.heappop(heap)
            if current in closed:
                continue
        else:
            current = frontier.popleft() if algorithm == "BFS" else frontier.pop()
            distance = distances[current]
        closed.add(current)
        explored.append(current)
        if current == maze.goal:
            break
        for neighbor in maze.neighbors(current):
            new_distance = distance + 1
            if algorithm == "A*":
                if new_distance >= distances.get(neighbor, float("inf")):
                    continue
                h = abs(neighbor[0] - maze.goal[0]) + abs(neighbor[1] - maze.goal[1])
                heapq.heappush(heap, (new_distance + h, new_distance, neighbor))
            else:
                if neighbor in parent:
                    continue
                frontier.append(neighbor)
            parent[neighbor] = current
            distances[neighbor] = new_distance
    path = []
    if maze.goal in closed:
        current = maze.goal
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
    return SearchResult(algorithm, path, explored, (perf_counter() - started) * 1000)
