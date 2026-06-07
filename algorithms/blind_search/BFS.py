from collections import deque
from models.state import State

def bfs_search(start_state: State, target: int):
    """
   
    Trả về:
        path: list[(State, action)] từ start đến goal, hoặc None nếu không tìm thấy.
        expanded_count: số trạng thái mở rộng.
    """
    if start_state.is_goal(target):
        return [(start_state, "Bắt đầu")], 0

    queue = deque([start_state])
    visited = set([start_state])
    parent = {start_state: (None, "Bắt đầu")}
    expanded_count = 0

    while queue:
        current = queue.popleft()
        expanded_count += 1

        if current.is_goal(target):
            # reconstruct path
            path = []
            while current is not None:
                prev, action = parent[current]
                path.append((current, action))
                current = prev
            path.reverse()
            return path, expanded_count

        for next_state, action in current.get_successors():
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = (current, action)
                queue.append(next_state)

    return None, expanded_count