"""Mini-project - A reusable graph toolkit for the course.

Save location: ``iskit/graph.py`` (here: ``ps00/iskit/graph.py``).
Reused in Sheets 2, 3, 5 and 10.

Features:
  * Adjacency-dictionary representation: ``self.adj = {u: {v: w, ...}, ...}``
  * Directed and undirected graphs, default weight 1.0, negative weights rejected.
  * Load from JSON text: ``{"directed": false, "edges": [["A", "B", 2.0], ...]}``
  * ``bfs`` (fewest edges), ``dijkstra`` (least cost), ``astar`` (heuristic search).

Conventions:
  * ``bfs(s, goal)`` returns ``(path, nodes_expanded)``.
    ``path`` is a list of nodes from ``s`` to ``goal`` (inclusive),
    or ``None`` if the goal is unreachable.
    ``nodes_expanded`` is the number of nodes popped from the FIFO queue.
  * ``dijkstra(s, goal)`` / ``astar(s, goal, h)`` return ``(path, cost)``.
    ``path`` is ``None`` and ``cost`` is ``float('inf')`` if unreachable.
"""

from __future__ import annotations

import heapq
import json
from collections import deque
from typing import Callable, Dict, Iterable, List, Optional, Tuple


class Graph:
    """Weighted, directed or undirected graph stored as an adjacency dictionary."""

    def __init__(self, directed: bool = False):
        self.adj: Dict[str, Dict[str, float]] = {}
        self.directed: bool = bool(directed)

    # ------------------------------------------------------------------ basics
    def add_node(self, u: str) -> None:
        """Ensure node ``u`` exists (even with no outgoing edges)."""
        self.adj.setdefault(u, {})

    def add_edge(self, u: str, v: str, w: float = 1.0) -> None:
        """Add edge u -> v with weight w (both ways if undirected).

        Raises:
            ValueError: if ``w`` is negative.
            TypeError: if ``w`` is not a number.
        """
        try:
            w = float(w)
        except (TypeError, ValueError) as e:
            raise TypeError(f"weight must be a number, got {w!r}") from e
        if w < 0:
            raise ValueError(f"negative weight not allowed: {u!r} -> {v!r} weight={w}")
        self.adj.setdefault(u, {})[v] = w
        self.adj.setdefault(v, {})  # track v as a node even if it has no outgoing edges
        if not self.directed:
            self.adj.setdefault(v, {})[u] = w

    def neighbors(self, u: str) -> Iterable[Tuple[str, float]]:
        """Iterable of (v, w) pairs for outgoing edges of ``u``."""
        return list(self.adj.get(u, {}).items())

    def nodes(self) -> List[str]:
        """List of all known nodes."""
        return list(self.adj.keys())

    def __contains__(self, u: str) -> bool:
        return u in self.adj

    def __len__(self) -> int:
        return len(self.adj)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        kind = "directed" if self.directed else "undirected"
        n_edges = sum(len(v) for v in self.adj.values())
        if not self.directed:
            n_edges //= 2
        return f"Graph({kind}, nodes={len(self.adj)}, edges={n_edges})"

    # ---------------------------------------------------------------- JSON I/O
    @classmethod
    def from_json(cls, text: str) -> "Graph":
        """Build a Graph from JSON text.

        Expected format::

            {"directed": false, "edges": [["A", "B", 2.0], ["B", "C"], ...]}

        * ``directed`` is optional (defaults to False).
        * Each edge is ``[u, v]`` (weight defaults to 1.0) or ``[u, v, w]``.
        * Negative weights are rejected (ValueError).

        Raises:
            ValueError: on invalid JSON or bad schema.
        """
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"invalid JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("JSON must be an object like {'directed': bool, 'edges': [...]}")
        if "edges" not in data:
            raise ValueError("JSON missing required key 'edges'")
        directed = data.get("directed", False)
        edges = data["edges"]
        if not isinstance(directed, bool):
            raise ValueError("'directed' must be a boolean")
        if not isinstance(edges, list):
            raise ValueError("'edges' must be a list of [u, v] or [u, v, w]")

        g = cls(directed=directed)
        for i, e in enumerate(edges):
            if not isinstance(e, (list, tuple)) or len(e) not in (2, 3):
                raise ValueError(f"edge #{i} must be [u, v] or [u, v, w], got {e!r}")
            u, v = e[0], e[1]
            w = e[2] if len(e) == 3 else 1.0
            if not isinstance(u, str) or not isinstance(v, str):
                raise ValueError(f"edge #{i} endpoints must be strings, got {e!r}")
            # add_edge raises ValueError on negative weight / TypeError on bad weight
            try:
                g.add_edge(u, v, w)
            except (ValueError, TypeError) as ex:
                raise ValueError(f"edge #{i} {e!r}: {ex}") from ex
        return g

    def to_json(self) -> str:
        """Serialize back to the same JSON format (useful for round-trip tests)."""
        seen = set()
        edges = []
        for u, nbrs in self.adj.items():
            for v, w in nbrs.items():
                if not self.directed and (v, u) in seen:
                    continue
                edges.append([u, v, w])
                seen.add((u, v))
        return json.dumps({"directed": self.directed, "edges": edges})

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _reconstruct(parent: Dict[str, Optional[str]], s: str, goal: str) -> List[str]:
        path = [goal]
        cur = goal
        while cur != s:
            cur = parent[cur]  # type: ignore[index]
            path.append(cur)
        path.reverse()
        return path

    # ------------------------------------------------------------------- search
    def bfs(self, s: str, goal: str) -> Tuple[Optional[List[str]], int]:
        """Breadth-first search: path with fewest edges (ignores weights).

        Returns:
            (path, nodes_expanded): path is None if goal unreachable.
        """
        if s == goal:
            return ([s], 0) if s in self.adj else (None, 0)
        if s not in self.adj or goal not in self.adj:
            return None, 0

        visited = {s}
        parent: Dict[str, Optional[str]] = {s: None}
        q: deque[str] = deque([s])
        expanded = 0
        while q:
            u = q.popleft()
            expanded += 1
            for v in self.adj.get(u, {}):
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    if v == goal:
                        return self._reconstruct(parent, s, goal), expanded
                    q.append(v)
        return None, expanded

    def dijkstra(self, s: str, goal: str) -> Tuple[Optional[List[str]], float]:
        """Dijkstra (uniform-cost): least-cost path using a heapq priority queue.

        Returns:
            (path, cost): (None, inf) if goal unreachable.
        """
        if s == goal:
            return ([s], 0.0) if s in self.adj else (None, float("inf"))
        if s not in self.adj or goal not in self.adj:
            return None, float("inf")

        dist: Dict[str, float] = {s: 0.0}
        parent: Dict[str, Optional[str]] = {s: None}
        pq: list[Tuple[float, str]] = [(0.0, s)]
        closed: set[str] = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in closed:
                continue
            closed.add(u)
            if u == goal:
                return self._reconstruct(parent, s, goal), d
            if d > dist.get(u, float("inf")):
                continue
            for v, w in self.adj.get(u, {}).items():
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    parent[v] = u
                    heapq.heappush(pq, (nd, v))
        return None, float("inf")

    def astar(
        self, s: str, goal: str, h: Callable[[str], float]
    ) -> Tuple[Optional[List[str]], float]:
        """A* search: Dijkstra guided by heuristic ``h(node) -> estimate``.

        ``h`` should be non-negative and ideally admissible (never overestimates)
        so the returned path is optimal. ``h(goal)`` should be 0.

        Returns:
            (path, cost): (None, inf) if goal unreachable.
        """
        if s == goal:
            return ([s], 0.0) if s in self.adj else (None, float("inf"))
        if s not in self.adj or goal not in self.adj:
            return None, float("inf")

        g_score: Dict[str, float] = {s: 0.0}
        parent: Dict[str, Optional[str]] = {s: None}
        pq: list[Tuple[float, float, str]] = [(float(h(s)), 0.0, s)]  # (f, g, node)
        closed: set[str] = set()

        while pq:
            _, g, u = heapq.heappop(pq)
            if u in closed:
                continue
            closed.add(u)
            if u == goal:
                return self._reconstruct(parent, s, goal), g
            if g > g_score.get(u, float("inf")):
                continue
            for v, w in self.adj.get(u, {}).items():
                ng = g + w
                if ng < g_score.get(v, float("inf")):
                    g_score[v] = ng
                    parent[v] = u
                    heapq.heappush(pq, (ng + float(h(v)), ng, v))
        return None, float("inf")
