from collections import deque

def find_join_path(graph, start, end):
    if start == end:
        return [start]

    visited = set()
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()

        if node in visited:
            continue

        visited.add(node)

        for neighbor in graph.get(node, []):
            if neighbor == end:
                return path + [neighbor]

            queue.append((neighbor, path + [neighbor]))

    return None