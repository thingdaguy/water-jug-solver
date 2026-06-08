# Greedy.py
import heapq
from models.state import State
from algorithms.informed_search.Heuristic import heuristic_estimate

def greedy_search(start_state: State, target: int, heuristic_fn=heuristic_estimate):
    """
    Thuật toán tìm kiếm tham lam (Greedy Best-First Search).
    Trả về:
        path: Danh sách các cặp (State, mô_tả_hành_động) từ trạng thái đầu đến đích, hoặc None nếu không tìm thấy.
        expanded_count: Tổng số trạng thái đã mở rộng.
        visited_states: Set các trạng thái đã duyệt.
        frontier_states: Set các trạng thái trong biên chưa duyệt.
        parent_map: Dict lưu vết (child -> (parent, action)).
    """
    counter = 0
    start_h = heuristic_fn(start_state, target)
    
    # Frontier lưu: (h_val, counter, current_state)
    frontier = []
    heapq.heappush(frontier, (start_h, counter, start_state))
    
    parent_map = {start_state: (None, "Bắt đầu")}
    visited = set()
    expanded_count = 0

    while frontier:
        h, _, current_state = heapq.heappop(frontier)

        if current_state in visited:
            continue
            
        visited.add(current_state)
        expanded_count += 1

        if current_state.is_goal(target):
            # Dựng lại đường đi
            path = []
            curr = current_state
            while curr is not None:
                prev, action = parent_map[curr]
                path.append((curr, action))
                curr = prev
            path.reverse()
            
            frontier_states = set(item[2] for item in frontier if item[2] not in visited)
            return path, expanded_count, visited, frontier_states, parent_map

        for next_state, action in current_state.get_successors():
            if next_state not in visited:
                if next_state not in parent_map:
                    parent_map[next_state] = (current_state, action)
                    next_h = heuristic_fn(next_state, target)
                    counter += 1
                    heapq.heappush(frontier, (next_h, counter, next_state))

    frontier_states = set(item[2] for item in frontier if item[2] not in visited)
    return None, expanded_count, visited, frontier_states, parent_map
