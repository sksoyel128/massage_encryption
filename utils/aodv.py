# utils/aodv.py
from collections import deque
from typing import List, Optional

def _adj_matrix_to_adj_list(adj_matrix: List[List[int]]):
    """Convert adjacency matrix (0 or None = no edge, positive cost = edge) to adjacency list."""
    n = len(adj_matrix)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(n):
            cost = adj_matrix[i][j]
            if cost and cost > 0:
                adj[i].append(j)
    return adj

def aodv(adj_matrix: List[List[int]], src: int, dst: int) -> Optional[List[int]]:
    """
    Simplified AODV-like route discovery using BFS flood (no sequence numbers/timers).
    Returns list of node indices from src..dst or None if unreachable.
    This is a simulation for a single-process environment (no sockets).
    """
    if src == dst:
        return [src]

    adj = _adj_matrix_to_adj_list(adj_matrix)
    # BFS keeping parent map (simulate RREQ flood)
    q = deque([src])
    parent = {src: None}
    found = False
    while q:
        u = q.popleft()
        for v in adj.get(u, []):
            if v not in parent:
                parent[v] = u
                if v == dst:
                    found = True
                    q.clear()
                    break
                q.append(v)
    if not found:
        return None
    # reconstruct path
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
