
from models.state import State

def dfs_search(start_state: State, target: int):
    """
    - Dùng visited toàn cục để tránh lặp trạng thái.
    - Lưu parent dict để reconstruct path.
    Trả về:
        path: list[(State, action)] từ start đến goal, hoặc None nếu không tìm thấy.
        expanded_count: số trạng thái thực sự được mở rộng.
    """
    stack = [start_state]
    visited = set([start_state])
    parent = {start_state: (None, "Bắt đầu")}
    expanded_count = 0

    while stack:
        current = stack.pop()
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

        for next_state, action in reversed(current.get_successors()):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = (current, action)
                stack.append(next_state)

    return None, expanded_count
