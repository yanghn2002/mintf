from typing import *
import heapq
from .frame import *


class Chain:

    def __init__(self, tfs:Sequence[Tuple[Frame, bool]]) -> None:

        self.__tfs = tfs
    
    def __call__(self) -> Frame:

        frame = Frame()

        for f, i in self.__tfs:
            frame(f, inv=True if i else False)

        return frame


class Graph:
    
    def __init__(self, *args) -> None:

        self.__graph = {}
        self.__cache = {}

        for source, target, frame in args:
            if source not in self.__graph: self.__graph[source] = {}
            if target not in self.__graph: self.__graph[target] = {}
            self.__graph[source][target] = (frame, False)
            self.__graph[target][source] = (frame, True) # inverse

    def __call__(self, source:Hashable, target:Hashable) -> list:

        key = (source, target)

        if key in self.__cache: return self.__cache[key]

        queue = [(0, source, [])]
        visited = set()
        while queue:
            dist, node, path = heapq.heappop(queue)
            if node in visited: continue
            visited.add(node)
            path = path + [node]
            if node == target:
                chain = Chain(
                    [self.__graph[path[i]][path[i+1]] for i in range(len(path)-1)]
                )
                self.__cache[key] = chain
                return chain
            for neighbor in self.__graph.get(node, {}):
                if neighbor not in visited:
                    heapq.heappush(queue, (dist+1, neighbor, path))
        raise RuntimeError(f"'{source}' -> '{target}' is not reachable")