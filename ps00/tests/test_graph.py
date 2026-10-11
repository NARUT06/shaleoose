"""Assert-based tests for iskit/graph.py (Sheet 0, Part C).

Run from ``ps00/`` with:
    python -m pytest tests/test_graph.py -v
or without pytest:
    python tests/test_graph.py
    python -m tests.test_graph
"""

import json
import math
import sys
from pathlib import Path

# allow running as script: python tests/test_graph.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from iskit.graph import Graph


def make_basic() -> Graph:
    # Undirected diamond where fewest-hops != cheapest:
    #   A-B (1), B-D (1), A-C (1), C-D (10)
    # BFS A->D : 2 hops (either side). Dijkstra A->D : A-B-D cost 2.
    g = Graph(directed=False)
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "D", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("C", "D", 10.0)
    return g


def test_undirected_symmetry_and_default_weight():
    g = Graph(directed=False)
    g.add_edge("X", "Y")  # default weight 1.0
    assert dict(g.neighbors("X")) == {"Y": 1.0}
    assert dict(g.neighbors("Y")) == {"X": 1.0}, "undirected must add reverse edge"


def test_directed_no_reverse():
    g = Graph(directed=True)
    g.add_edge("A", "B", 2.0)
    assert dict(g.neighbors("A")) == {"B": 2.0}
    assert dict(g.neighbors("B")) == {}, "directed must NOT add reverse edge"
    # reverse direction is unreachable
    path, _ = g.bfs("B", "A")
    assert path is None


def test_negative_weight_rejected():
    g = Graph()
    try:
        g.add_edge("A", "B", -1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative weight must raise ValueError")
    # via JSON too
    bad = json.dumps({"directed": False, "edges": [["A", "B", -5]]})
    try:
        Graph.from_json(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("from_json with negative weight must raise ValueError")


def test_from_json_round_trip():
    text = json.dumps({"directed": False, "edges": [["A", "B", 2.0], ["B", "C"]]})
    g = Graph.from_json(text)
    assert g.directed is False
    assert dict(g.neighbors("A")) == {"B": 2.0}
    # ["B","C"] defaults to weight 1.0
    assert dict(g.neighbors("B"))["C"] == 1.0
    # directed flag respected
    gd = Graph.from_json(json.dumps({"directed": True, "edges": [["A", "B", 1]]}))
    assert gd.directed is True
    assert dict(gd.neighbors("B")) == {}


def test_invalid_json():
    for bad in ["not json at all", '{"no_edges": []}', '{"edges": "oops"}',
                '{"edges": [["A"]]}', '{"edges": [[[1, 2, 3]]]}']:
        try:
            Graph.from_json(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid JSON must raise ValueError: {bad!r}")


def test_bfs_fewest_edges():
    g = make_basic()
    path, expanded = g.bfs("A", "D")
    assert path is not None and path[0] == "A" and path[-1] == "D"
    assert len(path) == 3, f"BFS must use 2 hops, got {path}"
    assert expanded >= 2
    # start == goal
    p0, _ = g.bfs("A", "A")
    assert p0 == ["A"]


def test_dijkstra_least_cost():
    g = make_basic()
    path, cost = g.dijkstra("A", "D")
    assert path == ["A", "B", "D"], f"Dijkstra must avoid expensive C-D edge, got {path}"
    assert cost == 2.0, f"expected cost 2.0, got {cost}"
    # start == goal
    p0, c0 = g.dijkstra("A", "A")
    assert p0 == ["A"] and c0 == 0.0


def test_astar_matches_dijkstra():
    g = make_basic()
    # admissible heuristic: never overestimates true cost to D
    h = {"A": 1.0, "B": 1.0, "C": 5.0, "D": 0.0}
    path, cost = g.astar("A", "D", lambda n: h[n])
    assert path == ["A", "B", "D"], f"A* path wrong: {path}"
    assert cost == 2.0
    # zero heuristic == Dijkstra
    _, d_cost = g.dijkstra("A", "D")
    _, a_cost = g.astar("A", "D", lambda n: 0.0)
    assert a_cost == d_cost == 2.0


def test_unreachable_goal():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_node("Z")  # isolated node
    # BFS
    path, _ = g.bfs("A", "Z")
    assert path is None, "BFS unreachable must return None"
    # Dijkstra
    d_path, d_cost = g.dijkstra("A", "Z")
    assert d_path is None and math.isinf(d_cost)
    # A*
    a_path, a_cost = g.astar("A", "Z", lambda n: 0.0)
    assert a_path is None and math.isinf(a_cost)
    # unknown nodes entirely
    assert g.bfs("NOPE", "Z")[0] is None
    assert math.isinf(g.dijkstra("A", "NOPE")[1])


def run_all():
    test_undirected_symmetry_and_default_weight()
    test_directed_no_reverse()
    test_negative_weight_rejected()
    test_from_json_round_trip()
    test_invalid_json()
    test_bfs_fewest_edges()
    test_dijkstra_least_cost()
    test_astar_matches_dijkstra()
    test_unreachable_goal()
    print("All 9 tests passed.")


if __name__ == "__main__":
    run_all()
