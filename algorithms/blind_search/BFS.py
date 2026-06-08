from collections import deque
from models.state import State

def bfs_search(start_state: State, target: int):
    """
    Tìm kiếm theo chiều rộng (BFS).
    Trả về:
        path: list[(State, action)] từ start đến goal, hoặc None nếu không tìm thấy.
        expanded_count: số trạng thái mở rộng.
        visited_states: set các trạng thái đã mở rộng (đã lấy ra khỏi hàng đợi).
        frontier_states: set các trạng thái nằm trong hàng đợi mà chưa mở rộng.
        parent_map: dict lưu vết (child -> (parent, action)).
    """
    if start_state.is_goal(target):
        parent_map = {start_state: (None, "Bắt đầu")}
        return [(start_state, "Bắt đầu")], 0, {start_state}, set(), parent_map

    queue = deque([start_state])
    enqueued = {start_state}
    expanded = set()
    parent = {start_state: (None, "Bắt đầu")}

    while queue:
        current = queue.popleft()
        expanded.add(current)

        if current.is_goal(target):
            path = []
            curr = current
            while curr is not None:
                prev, action = parent[curr]
                path.append((curr, action))
                curr = prev
            path.reverse()
            return path, len(expanded), expanded, set(queue), parent

        for next_state, action in current.get_successors():
            if next_state not in enqueued:
                enqueued.add(next_state)
                parent[next_state] = (current, action)
                queue.append(next_state)

    return None, len(expanded), expanded, set(queue), parent
