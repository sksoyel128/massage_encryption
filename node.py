from typing import List, Tuple, Optional
from encryption import AESCipher
from utils.dijkstra import dijkstra, dijkstra_with_edge_exclusion
from utils.aodv import aodv as aodv_func
from Crypto.Random import get_random_bytes

class Node:
    def __init__(self, node_id: int):
        self.node_id = node_id
        # You can add more node-specific attributes here if needed

class Network:
    def __init__(self, size: int = 10, routing_algo: str = "dijkstra", persist_sessions: bool = False):
        self.size = size
        self.nodes = [Node(i) for i in range(size)]
        self.routing_algo = routing_algo.lower()
        self.adj_matrix = [
            [0, 2, 0, 0, 0, 0, 0, 0, 0, 5],
            [2, 0, 3, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 4, 0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 6, 0, 0, 0, 0, 0],
            [0, 0, 0, 6, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 0, 7, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 8, 0, 9],
            [5, 0, 0, 0, 0, 0, 0, 0, 9, 0],
        ]
        if len(self.adj_matrix) != size:
            raise ValueError("Adjacency matrix size and network size mismatch.")
        self.persist_sessions = persist_sessions
        self.session_store = {}

    def _get_path(self, src: int, dst: int) -> Optional[List[int]]:
        if self.routing_algo == "aodv":
            return aodv_func(self.adj_matrix, src, dst)
        return dijkstra(self.adj_matrix, src, dst)

    def find_all_paths(self, start: int, end: int, path=None) -> List[List[int]]:
        if path is None:
            path = []
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        for node, cost in enumerate(self.adj_matrix[start]):
            if cost and node not in path:
                new_paths = self.find_all_paths(node, end, path)
                for p in new_paths:
                    paths.append(p)
        return paths

    def _create_session_key(self, src: int, dst: int) -> bytes:
        if self.persist_sessions:
            pair = (src, dst)
            if pair in self.session_store:
                return self.session_store[pair]
            key = get_random_bytes(32)
            self.session_store[pair] = key
            return key
        else:
            return get_random_bytes(32)

    def get_top_k_shortest_paths(self, src: int, dst: int, k: int = 3):
        paths = []
        excluded_edges = set()
        for _ in range(k):
            path, cost = dijkstra_with_edge_exclusion(self.adj_matrix, src, dst, excluded_edges)
            if path is None:
                break
            paths.append((path, cost))
            for i in range(len(path) - 1):
                excluded_edges.add((path[i], path[i+1]))
                excluded_edges.add((path[i+1], path[i]))
        return paths

    def send_message(self, src: int, dst: int, message: str) -> Tuple[List[int], List[str], Optional[str]]:
        logs: List[str] = []
        top_paths = self.get_top_k_shortest_paths(src, dst, k=3)
        if not top_paths:
            logs.append(f"No paths found from Node {src} to Node {dst}.")
            return [], logs, None
        logs.append(f"Top {len(top_paths)} shortest paths from Node {src} to Node {dst}:")
        for idx, (p, c) in enumerate(top_paths, 1):
            logs.append(f"  Path {idx}: {p} with cost {c}")
        path = top_paths[0][0]
        session_key = self._create_session_key(src, dst)
        cipher = AESCipher(key=session_key)
        ciphertext, iv = cipher.encrypt(message)
        logs.append(f"Session key (hex) for {src}->{dst}: {session_key.hex()}")
        logs.append(f"Encrypted at Node {src}: ciphertext(hex)={ciphertext.hex()} iv(hex)={iv.hex()}")
        for i in range(1, len(path)):
            cur = path[i - 1]
            nxt = path[i]
            cost = self.adj_matrix[cur][nxt]
            logs.append(f"Forwarded from Node {cur} → Node {nxt} (cost={cost})")
        try:
            dst_cipher = AESCipher(key=session_key)
            decrypted = dst_cipher.decrypt(ciphertext, iv)
            logs.append(f"Decrypted at Node {dst}: {decrypted}")
        except Exception as e:
            decrypted = None
            logs.append(f"Decryption failed at Node {dst}: {type(e).__name__}: {e}")
        return path, logs, decrypted

    def add_edge(self, node1: int, node2: int, cost: int):
        if 0 <= node1 < self.size and 0 <= node2 < self.size and cost > 0:
            self.adj_matrix[node1][node2] = cost
            self.adj_matrix[node2][node1] = cost
        else:
            raise ValueError("Invalid nodes or cost")

    def remove_edge(self, node1: int, node2: int):
        if 0 <= node1 < self.size and 0 <= node2 < self.size:
            self.adj_matrix[node1][node2] = 0
            self.adj_matrix[node2][node1] = 0
        else:
            raise ValueError("Invalid nodes")

    def set_node_offline(self, node: int):
        if 0 <= node < self.size:
            for i in range(self.size):
                self.adj_matrix[node][i] = 0
                self.adj_matrix[i][node] = 0
        else:
            raise ValueError("Invalid node")

    def set_node_online(self, node: int, connections: dict):
        if 0 <= node < self.size:
            for neighbor, cost in connections.items():
                if 0 <= neighbor < self.size and cost > 0:
                    self.adj_matrix[node][neighbor] = cost
                    self.adj_matrix[neighbor][node] = cost
                else:
                    raise ValueError("Invalid neighbor or cost")
        else:
            raise ValueError("Invalid node")
