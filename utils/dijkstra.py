import heapq
from typing import List, Set, Tuple, Optional

def dijkstra(graph: List[List[int]], src: int, dst: int) -> List[int]:
    n = len(graph)
    INF = float("inf")
    dist = [INF] * n
    prev = [-1] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        cost_u, u = heapq.heappop(heap)
        if cost_u > dist[u]:
            continue
        if u == dst:
            break
        for v in range(n):
            w = graph[u][v]
            if not w:
                continue
            new_cost = cost_u + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    if dist[dst] == INF:
        return []
    path = []
    cur = dst
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

def dijkstra_with_edge_exclusion(graph: List[List[int]], src: int, dst: int, excluded_edges: Set[Tuple[int, int]]) -> Tuple[Optional[List[int]], Optional[int]]:
    n = len(graph)
    INF = float("inf")
    dist = [INF] * n
    prev = [-1] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        cost_u, u = heapq.heappop(heap)
        if cost_u > dist[u]:
            continue
        if u == dst:
            break
        for v in range(n):
            w = graph[u][v]
            if not w:
                continue
            if (u, v) in excluded_edges or (v, u) in excluded_edges:
                continue
            new_cost = cost_u + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    if dist[dst] == INF:
        return None, None

    path = []
    cur = dst
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path, dist[dst]
