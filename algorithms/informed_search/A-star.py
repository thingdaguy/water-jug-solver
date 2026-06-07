# A-star.py
import heapq
from models.state import State
from algorithms.informed_search.Heuristic import heuristic

def a_star_search(start_state: State, target: int):
    """
    Thuật toán tìm kiếm A*.
    Trả về:
        path: Danh sách các cặp (State, mô_tả_hành_động) từ trạng thái đầu đến đích, hoặc None nếu không tìm thấy.
        expanded_count: Tổng số trạng thái đã mở rộng.
    """
    # Frontier: hàng đợi ưu tiên lưu trữ các phần tử dạng (f, counter, g, current_state, path)
    counter = 0
    start_g = 0
    start_h = heuristic(start_state, target)
    start_f = start_g + start_h
    
    frontier = []
    heapq.heappush(frontier, (start_f, counter, start_g, start_state, [(start_state, "Bắt đầu")]))
    
    # Lưu g-value tốt nhất tìm được cho từng trạng thái
    best_g = {start_state: start_g}
    expanded_count = 0

    while frontier:
        f, _, g, current_state, path = heapq.heappop(frontier)

        # Nếu đã tìm được một đường đi rẻ hơn đến trạng thái này, bỏ qua phần tử này
        if g > best_g.get(current_state, float('inf')):
            continue

        expanded_count += 1

        if current_state.is_goal(target):
            return path, expanded_count

        for next_state, action in current_state.get_successors():
            next_g = g + 1
            if next_g < best_g.get(next_state, float('inf')):
                best_g[next_state] = next_g
                next_h = heuristic(next_state, target)
                next_f = next_g + next_h
                counter += 1
                new_path = list(path) + [(next_state, action)]
                heapq.heappush(frontier, (next_f, counter, next_g, next_state, new_path))

    return None, expanded_count
