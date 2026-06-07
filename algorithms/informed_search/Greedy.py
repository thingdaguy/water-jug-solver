# Greedy.py
import heapq
from models.state import State
from algorithms.informed_search.Heuristic import heuristic

def greedy_search(start_state: State, target: int):
    """
    Thuật toán tìm kiếm tham lam (Greedy Best-First Search).
    Trả về:
        path: Danh sách các cặp (State, mô_tả_hành_động) từ trạng thái đầu đến đích, hoặc None nếu không tìm thấy.
        expanded_count: Tổng số trạng thái đã mở rộng.
    """
    # Frontier: hàng đợi ưu tiên lưu trữ các phần tử dạng (h, counter, current_state, path)
    # Sử dụng counter để giải quyết các trường hợp trùng giá trị heuristic nhằm tránh so sánh trực tiếp các đối tượng State.
    counter = 0
    start_h = heuristic(start_state, target)
    
    frontier = []
    heapq.heappush(frontier, (start_h, counter, start_state, [(start_state, "Bắt đầu")]))
    
    visited = set()
    expanded_count = 0

    while frontier:
        h, _, current_state, path = heapq.heappop(frontier)

        if current_state in visited:
            continue
            
        visited.add(current_state)
        expanded_count += 1

        if current_state.is_goal(target):
            return path, expanded_count

        for next_state, action in current_state.get_successors():
            if next_state not in visited:
                next_h = heuristic(next_state, target)
                counter += 1
                new_path = list(path) + [(next_state, action)]
                heapq.heappush(frontier, (next_h, counter, next_state, new_path))

    return None, expanded_count
