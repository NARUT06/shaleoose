# CSC4103 — Sheet 0 (Part C): Reusable Graph Toolkit

Small, well-tested `Graph` class reused in Sheets 2, 3, 5, 10.

## Layout

```text
ps00/
  iskit/
    __init__.py
    graph.py        # Graph: adjacency-dict, JSON loading, bfs/dijkstra/astar
  tests/
    test_graph.py   # 9 assert-based tests (normal + edge cases)
  README.md         # this file
```

## Requirements

- Python 3.10+
- No third-party dependencies for Part C (stdlib only: `json`, `heapq`, `collections`).

## How to run the tests

From `ps00/`:

```bash
# option 1 — no extra install (plain asserts)
python tests/test_graph.py

# option 2 — as a module
python -m tests.test_graph

# option 3 — pytest (if installed)
python -m pytest tests/test_graph.py -v
```

Expected output: `All 9 tests passed.`

## Quick use

```python
from iskit.graph import Graph

g = Graph.from_json('{"directed": false, "edges": [["A","B",2.0],["B","C",1.0]]}')
print(g.bfs("A", "C"))        # (['A','B','C'], expanded)
print(g.dijkstra("A", "C"))   # (['A','B','C'], 3.0)
print(g.astar("A", "C", lambda n: 0.0))
```

## API notes

- `add_edge(u, v, w=1.0)` rejects negative `w` with `ValueError`.
- `from_json(text)` expects `{"directed": bool, "edges": [[u,v,w?], ...]}`;
  raises `ValueError` on bad JSON/schema.
- `bfs(s, goal)` → `(path|None, nodes_expanded)` (fewest edges).
- `dijkstra(s, goal)` → `(path|None, cost|inf)` (least cost, `heapq`).
- `astar(s, goal, h)` → `(path|None, cost|inf)`; `h(node)` is the heuristic.
- Unreachable goal → `path is None` (`cost=inf` for dijkstra/astar).
